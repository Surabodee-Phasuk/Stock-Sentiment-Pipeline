"""F2-02: Spark Structured Streaming อ่านข่าวจาก Kafka `stock-news` แล้ว append ลง `raw_news`.

รันใน container `spark` (ต้องสร้างตารางด้วย F2-01 และตั้งค่า AWS แล้ว):
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit streaming/raw_news_stream.py

Raw เก็บทุก event ตามที่รับมา แม้อ่าน JSON ไม่ได้ (ฟิลด์ข่าวจะเป็น null แต่ `raw_value` ยังอยู่)
การตรวจและตัดข่าวซ้ำอยู่ที่ `clean_news` (F2-03)

checkpoint จำ offset ที่เขียนแล้ว และ commit คู่กับ snapshot ของ Iceberg
ถ้าหยุดแล้วรันใหม่จะอ่านต่อจากจุดเดิม ข่าวไม่หายและไม่ถูกเขียนซ้ำ (NFR-2)
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

DEFAULT_TABLE = "glue.stock_sentiment.raw_news"
DEFAULT_CHECKPOINT = "s3a://stock-sentiment-lakehouse-surabodee/checkpoints/raw_news"
NEWS_FIELDS = ("news_id", "ticker", "headline", "summary", "source", "url")
TIME_FIELDS = ("published_at", "ingested_at")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kafka stock-news -> raw_news")
    parser.add_argument(
        "--bootstrap-servers",
        default=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:19092"),
    )
    parser.add_argument("--topic", default=os.environ.get("KAFKA_TOPIC", "stock-news"))
    parser.add_argument("--table", default=DEFAULT_TABLE)
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument(
        "--trigger-seconds",
        type=int,
        default=60,
        help="micro-batch interval; ข่าวลงตารางช้าสุดเท่านี้หลังเข้า Kafka",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="อ่านข้อความที่มีอยู่ทั้งหมดแล้วจบ (availableNow)",
    )
    return parser


def to_raw_news(kafka_df):
    """แปลงแถวจาก Kafka ให้ตรงกับคอลัมน์ของ `raw_news` (ลำดับตาม lakehouse/ddl)."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType, StructField, StructType

    schema = StructType(
        [StructField(name, StringType()) for name in (*NEWS_FIELDS, *TIME_FIELDS)]
    )
    value = F.col("value").cast("string")
    parsed = F.from_json(value, schema)
    # try_to_timestamp: Spark 4 เปิด ANSI ไว้ ถ้าใช้ to_timestamp แถวที่เวลาผิดรูปจะทำให้ทั้ง job ล้ม
    return kafka_df.select(
        parsed.getField("news_id").alias("news_id"),
        F.coalesce(parsed.getField("ticker"), F.col("key").cast("string")).alias(
            "ticker"
        ),
        parsed.getField("headline").alias("headline"),
        parsed.getField("summary").alias("summary"),
        parsed.getField("source").alias("source"),
        parsed.getField("url").alias("url"),
        F.try_to_timestamp(parsed.getField("published_at")).alias("published_at"),
        F.try_to_timestamp(parsed.getField("ingested_at")).alias("ingested_at"),
        F.col("partition").alias("kafka_partition"),
        F.col("offset").alias("kafka_offset"),
        F.col("timestamp").alias("kafka_timestamp"),
        value.alias("raw_value"),
        F.current_timestamp().alias("loaded_at"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # import ตอนใช้ เพื่อให้ unit test ไม่ต้องมี pyspark
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("f2-02-raw-news-stream").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    kafka_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", args.bootstrap_servers)
        .option("subscribe", args.topic)
        .option("startingOffsets", "earliest")
        # Kafka เก็บข้อความ 7 วัน ถ้าหยุดนานกว่านั้น ให้อ่านต่อจากที่เหลือแทนการล้มทั้ง job
        .option("failOnDataLoss", "false")
        .load()
    )

    writer = (
        to_raw_news(kafka_df)
        .writeStream.format("iceberg")
        .outputMode("append")
        .option("checkpointLocation", args.checkpoint)
        # ไม่ต้องเรียงแถวตาม partition ก่อนเขียน แต่ละ micro-batch มีข่าวหลายวัน
        .option("fanout-enabled", "true")
    )
    if args.once:
        writer = writer.trigger(availableNow=True)
    else:
        writer = writer.trigger(processingTime=f"{args.trigger_seconds} seconds")

    query = writer.toTable(args.table)
    print(f"streaming {args.topic} -> {args.table}, checkpoint={args.checkpoint}")

    # ตอนไม่มีข้อมูล Spark รายงาน rows=0 ด้วย batchId ของรอบถัดไป จึงเทียบด้วย timestamp แทน batchId
    # ไม่เช่นนั้นรอบที่มีข้อมูลจริงจะมี batchId ซ้ำกับรอบว่างและไม่ถูกพิมพ์
    last_seen = None
    while query.isActive:
        query.awaitTermination(10)
        progress = query.lastProgress
        if not progress or progress["timestamp"] == last_seen:
            continue
        last_seen = progress["timestamp"]
        if progress["numInputRows"] > 0:
            print(
                f"batch={progress['batchId']} rows={progress['numInputRows']}",
                flush=True,
            )

    if query.exception():
        print(f"stream failed: {query.exception()}")
        return 1
    print("stream finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
