"""F3-04: reprocess sentiment ของข่าวทั้งหมดจาก `raw_news` ด้วย `model_version` ใหม่ (FR-2.6).

ใช้เมื่อเปลี่ยนโมเดลหรือวิธีสร้าง input: อ่านเฉพาะชั้น Raw ใน lakehouse ไม่ดึงข่าวจากแหล่งใหม่
ผลเดิมของ version อื่นยังอยู่ครบ (คีย์รวม model_version) เทียบผลระหว่าง version ได้

รันใน container `spark-ml`:
    docker compose -f infra/docker-compose.yml --profile ml run --rm spark-ml \
        /opt/spark/bin/spark-submit batch/reprocess/reprocess_sentiment.py \
        --model-version finbert-v2

    # เปลี่ยนเป็นโมเดลอื่นที่ให้ป้าย positive / neutral / negative เหมือนกัน
    ... reprocess_sentiment.py --model-name <hf-model> --model-version <ชื่อใหม่>

รันซ้ำได้: ข่าวที่มีผลของ version นี้แล้วจะถูกข้าม
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from sentiment.finbert import MODEL_NAME

DEFAULT_SOURCE = "glue.stock_sentiment.raw_news"
DEFAULT_TARGET = "glue.stock_sentiment.news_sentiment"
TICKERS_FILE = Path(__file__).resolve().parents[2] / "config" / "tickers.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="reprocess news_sentiment from raw")
    parser.add_argument("--model-version", required=True, help="เช่น finbert-v2")
    parser.add_argument("--model-name", default=MODEL_NAME)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--tickers-file", type=Path, default=TICKERS_FILE)
    parser.add_argument(
        "--since", type=date.fromisoformat, help="published_at >= (UTC)"
    )
    parser.add_argument("--until", type=date.fromisoformat, help="published_at < (UTC)")
    parser.add_argument("--batch-size", type=int, default=32)
    return parser


def date_filter(since: date | None, until: date | None) -> str | None:
    parts = []
    if since:
        parts.append(f"published_at >= TIMESTAMP '{since.isoformat()}'")
    if until:
        parts.append(f"published_at < TIMESTAMP '{until.isoformat()}'")
    return " AND ".join(parts) or None


def compare_versions(spark, target: str) -> None:
    spark.catalog.refreshTable(target)
    rows = spark.sql(
        "SELECT model_version, count(*) AS n, "
        "sum(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) AS pos, "
        "sum(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) AS neu, "
        "sum(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) AS neg, "
        "round(avg(sentiment_score), 3) AS avg_score "
        f"FROM {target} GROUP BY model_version ORDER BY model_version"
    ).collect()
    for r in rows:
        print(
            f"version={r['model_version']} rows={r['n']} positive={r['pos']} "
            f"neutral={r['neu']} negative={r['neg']} avg_score={r['avg_score']}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    from pyspark.sql import SparkSession

    from sentiment.finbert import FinBertClassifier
    from sentiment.pipeline import score_and_write, valid_unique_news
    from streaming.clean_news_job import load_tickers

    tickers = load_tickers(args.tickers_file)
    spark = SparkSession.builder.appName("f3-04-reprocess-sentiment").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    raw = spark.table(args.source)
    where = date_filter(args.since, args.until)
    if where:
        raw = raw.where(where)
    news = valid_unique_news(raw, tickers).cache()
    total = news.count()
    print(f"raw news to reprocess: {total} unique (news_id, ticker) from {args.source}")

    clf = FinBertClassifier(args.model_name, args.model_version, args.batch_size)
    started = time.perf_counter()
    stats = score_and_write(news, args.target, clf)
    news.unpersist()
    print(
        f"reprocess {args.model_name} as {args.model_version}: "
        + " ".join(f"{k}={v}" for k, v in stats.items())
        + f" skipped_existing={total - stats['scored']}"
        + f" total_seconds={time.perf_counter() - started:.1f}"
    )
    compare_versions(spark, args.target)
    print("reprocess finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
