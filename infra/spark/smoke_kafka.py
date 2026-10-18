"""INFRA-03 smoke test: Spark ใน container อ่าน topic `stock-news` จาก Kafka ได้ (batch read).

รันใน container หลังมีข้อความใน topic แล้ว (เช่นรัน collector หนึ่งรอบ):
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit infra/spark/smoke_kafka.py
"""

from __future__ import annotations

import os

from pyspark.sql import SparkSession


def main() -> int:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:19092")
    topic = os.environ.get("KAFKA_TOPIC", "stock-news")

    spark = SparkSession.builder.appName("infra03-smoke-kafka").getOrCreate()
    df = (
        spark.read.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap)
        .option("subscribe", topic)
        .option("startingOffsets", "earliest")
        .option("endingOffsets", "latest")
        .load()
        .selectExpr(
            "CAST(key AS STRING) AS ticker",
            "partition",
            "offset",
            "CAST(value AS STRING) AS value",
        )
    )

    total = df.count()
    print(f"topic={topic} messages={total}")
    df.groupBy("ticker").count().orderBy("ticker").show(50)
    df.show(3, truncate=100)
    if total == 0:
        raise SystemExit(f"no messages in {topic} — produce something first")

    print("kafka smoke test passed")
    spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
