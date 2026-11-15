"""F2-03: ตัดข่าวซ้ำและตรวจข้อมูล จาก `raw_news` เข้า `clean_news` ด้วย MERGE (FR-2.3, NFR-4).

รันใน container `spark` (ต้องมี `raw_news` จาก F2-02 แล้ว):
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit streaming/clean_news_job.py --once

อ่าน `raw_news` แบบ streaming (เฉพาะ snapshot ใหม่ที่ยังไม่เคยอ่าน จำไว้ใน checkpoint)
แต่ละรอบ: ตัดแถวที่ไม่ผ่านการตรวจ → เก็บแถวแรกที่เจอของแต่ละ (news_id, ticker)
→ MERGE ลง `clean_news` ด้วยคีย์ (news_id, ticker) แบบเพิ่มเฉพาะที่ยังไม่มี (ADR-0007)
รันซ้ำหรือ raw มีข่าวซ้ำกี่ครั้ง clean ก็มีหนึ่งแถวต่อคีย์เสมอ
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from pathlib import Path

DEFAULT_SOURCE = "glue.stock_sentiment.raw_news"
DEFAULT_TARGET = "glue.stock_sentiment.clean_news"
DEFAULT_CHECKPOINT = "s3a://stock-sentiment-lakehouse-surabodee/checkpoints/clean_news"
TICKERS_FILE = Path(__file__).resolve().parents[1] / "config" / "tickers.yaml"
# คอลัมน์ตามลำดับใน lakehouse/ddl/03_clean_news.sql
CLEAN_COLUMNS = (
    "news_id",
    "ticker",
    "headline",
    "summary",
    "source",
    "url",
    "published_at",
    "ingested_at",
    "cleaned_at",
)
EARLIEST_PUBLISHED = "2000-01-01"
FUTURE_TOLERANCE_HOURS = 1
_TICKER_LINE = re.compile(r"^\s*-\s*ticker:\s*([A-Z][A-Z.\-]{0,9})\s*$", re.MULTILINE)


def load_tickers(path: Path = TICKERS_FILE) -> list[str]:
    """อ่าน ticker จาก config/tickers.yaml โดยไม่ต้องลง PyYAML ใน container ของ Spark."""
    tickers = _TICKER_LINE.findall(Path(path).read_text(encoding="utf-8"))
    if not tickers:
        raise ValueError(f"no tickers in {path}")
    return tickers


def reject_reason_sql(tickers: Sequence[str]) -> str:
    """SQL ที่ให้เหตุผลที่ไม่รับแถว หรือ NULL ถ้าแถวนี้ผ่านการตรวจ."""
    allowed = ", ".join(f"'{t}'" for t in tickers)
    return (
        "CASE "
        "WHEN news_id IS NULL OR trim(news_id) = '' "
        "OR ticker IS NULL OR trim(ticker) = '' "
        "OR headline IS NULL OR trim(headline) = '' "
        "OR url IS NULL OR trim(url) = '' THEN 'missing_field' "
        "WHEN published_at IS NULL "
        f"OR published_at < TIMESTAMP '{EARLIEST_PUBLISHED}' "
        f"OR published_at > loaded_at + INTERVAL {FUTURE_TOLERANCE_HOURS} HOURS "
        "THEN 'bad_timestamp' "
        f"WHEN ticker NOT IN ({allowed}) THEN 'unknown_ticker' "
        "END"
    )


def merge_sql(target: str, updates_view: str) -> str:
    return (
        f"MERGE INTO {target} t USING {updates_view} s "
        "ON t.news_id = s.news_id AND t.ticker = s.ticker "
        "WHEN NOT MATCHED THEN INSERT *"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="raw_news -> clean_news (MERGE)")
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument("--tickers-file", type=Path, default=TICKERS_FILE)
    parser.add_argument("--trigger-seconds", type=int, default=60)
    parser.add_argument(
        "--once",
        action="store_true",
        help="ประมวลผลข่าวใน raw ที่ยังไม่เคยอ่านทั้งหมดแล้วจบ (availableNow)",
    )
    return parser


def make_batch_handler(target: str, tickers: Sequence[str]):
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    reason = reject_reason_sql(tickers)

    def handle(batch_df, batch_id: int) -> None:
        tagged = batch_df.withColumn("reject_reason", F.expr(reason)).cache()
        raw_rows = tagged.count()
        if raw_rows == 0:
            tagged.unpersist()
            return
        rejected = {
            r["reject_reason"]: r["count"]
            for r in tagged.where("reject_reason IS NOT NULL")
            .groupBy("reject_reason")
            .count()
            .collect()
        }

        # แถวแรกที่เจอของแต่ละคีย์ = แหล่งแรกและ ingested_at แรก
        first_seen = Window.partitionBy("news_id", "ticker").orderBy(
            F.col("ingested_at").asc_nulls_last(),
            F.col("kafka_timestamp").asc_nulls_last(),
            F.col("kafka_offset").asc_nulls_last(),
        )
        updates = (
            tagged.where("reject_reason IS NULL")
            .withColumn("_rn", F.row_number().over(first_seen))
            .where("_rn = 1")
            .withColumn("cleaned_at", F.current_timestamp())
            .select(*CLEAN_COLUMNS)
        )
        unique_keys = updates.count()

        spark = batch_df.sparkSession
        before = spark.table(target).count()
        updates.createOrReplaceTempView("clean_news_updates")
        spark.sql(merge_sql(target, "clean_news_updates"))
        inserted = spark.table(target).count() - before
        tagged.unpersist()

        print(
            f"batch={batch_id} raw_rows={raw_rows} rejected={rejected or 0} "
            f"unique_keys={unique_keys} inserted={inserted} "
            f"already_in_clean={unique_keys - inserted}",
            flush=True,
        )

    return handle


def report(spark, target: str) -> None:
    row = spark.sql(
        f"SELECT count(*) AS n, count(DISTINCT news_id, ticker) AS k FROM {target}"
    ).first()
    duplicates = row["n"] - row["k"]
    rate = duplicates / row["n"] * 100 if row["n"] else 0.0
    print(
        f"clean_news rows={row['n']} unique (news_id, ticker)={row['k']} "
        f"duplicates={duplicates} duplicate_rate={rate:.2f}%"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tickers = load_tickers(args.tickers_file)

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("f2-03-clean-news").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    writer = (
        spark.readStream.format("iceberg")
        .load(args.source)
        .writeStream.foreachBatch(make_batch_handler(args.target, tickers))
        .option("checkpointLocation", args.checkpoint)
    )
    if args.once:
        writer = writer.trigger(availableNow=True)
    else:
        writer = writer.trigger(processingTime=f"{args.trigger_seconds} seconds")

    query = writer.start()
    print(
        f"cleaning {args.source} -> {args.target} ({len(tickers)} tickers), "
        f"checkpoint={args.checkpoint}"
    )
    query.awaitTermination()
    if query.exception():
        print(f"job failed: {query.exception()}")
        return 1
    report(spark, args.target)
    print("job finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
