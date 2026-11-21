"""F3-01: ข่าวใหม่ใน `raw_news` → FinBERT → `news_sentiment` แบบ streaming (FR-3.1).

รันใน container `spark-ml` (image ที่มี torch + transformers, ดู infra/README.md):
    docker compose -f infra/docker-compose.yml --profile ml run --rm spark-ml \
        /opt/spark/bin/spark-submit streaming/news_sentiment_job.py --once

อ่าน `raw_news` แบบ streaming (ตารางนี้ append อย่างเดียว อ่าน snapshot ใหม่ได้ตรงๆ)
แต่ละรอบ: ตรวจและตัดซ้ำด้วยกฎของ F2-03 → ตัดข่าวที่มีผลของ model_version นี้แล้ว
→ FinBERT บน driver → MERGE ด้วยคีย์ (news_id, ticker, model_version)
รันซ้ำหรือข่าวซ้ำกี่ครั้ง ข่าวหนึ่งข่าวต่อหุ้นต่อเวอร์ชันมีผลเดียวเสมอ
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from sentiment.finbert import MODEL_NAME, MODEL_VERSION

DEFAULT_SOURCE = "glue.stock_sentiment.raw_news"
DEFAULT_TARGET = "glue.stock_sentiment.news_sentiment"
DEFAULT_CHECKPOINT = (
    "s3a://stock-sentiment-lakehouse-surabodee/checkpoints/news_sentiment"
)
TICKERS_FILE = Path(__file__).resolve().parents[1] / "config" / "tickers.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="raw_news -> FinBERT -> news_sentiment"
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument("--tickers-file", type=Path, default=TICKERS_FILE)
    parser.add_argument("--model-name", default=MODEL_NAME)
    parser.add_argument("--model-version", default=MODEL_VERSION)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--trigger-seconds", type=int, default=60)
    parser.add_argument(
        "--once",
        action="store_true",
        help="ประมวลผลข่าวใน raw ที่ยังไม่เคยอ่านทั้งหมดแล้วจบ (availableNow)",
    )
    return parser


def make_batch_handler(target: str, tickers: Sequence[str], clf):
    from sentiment.pipeline import score_and_write, valid_unique_news

    def handle(batch_df, batch_id: int) -> None:
        news = valid_unique_news(batch_df, tickers).cache()
        if news.isEmpty():
            news.unpersist()
            return
        stats = score_and_write(news, target, clf)
        news.unpersist()
        print(
            f"batch={batch_id} " + " ".join(f"{k}={v}" for k, v in stats.items()),
            flush=True,
        )

    return handle


def report(spark, target: str, model_version: str) -> None:
    # foreachBatch เขียนผ่าน session อื่น ต้อง refresh ก่อนอ่านสรุป ไม่งั้นได้ snapshot เก่า
    spark.catalog.refreshTable(target)
    rows = spark.sql(
        f"SELECT sentiment, count(*) AS n, round(avg(sentiment_score), 3) AS avg_score "
        f"FROM {target} WHERE model_version = '{model_version}' "
        "GROUP BY sentiment ORDER BY sentiment"
    ).collect()
    total = sum(r["n"] for r in rows)
    keys = spark.sql(
        f"SELECT count(DISTINCT news_id, ticker) AS k FROM {target} "
        f"WHERE model_version = '{model_version}'"
    ).first()["k"]
    detail = " ".join(f"{r['sentiment']}={r['n']}(avg {r['avg_score']})" for r in rows)
    print(
        f"news_sentiment[{model_version}] rows={total} unique (news_id, ticker)={keys} "
        f"duplicates={total - keys} {detail}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    from pyspark.sql import SparkSession

    from sentiment.finbert import FinBertClassifier
    from streaming.clean_news_job import load_tickers

    tickers = load_tickers(args.tickers_file)
    clf = FinBertClassifier(args.model_name, args.model_version, args.batch_size)
    clf.predict(["warm up"])  # โหลดโมเดลก่อนเริ่ม stream เวลาโหลดไม่ปนกับรอบแรก
    print(f"loaded {clf.model_name} ({clf.model_version}) in {clf.load_seconds:.1f}s")

    spark = SparkSession.builder.appName("f3-01-news-sentiment").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    writer = (
        spark.readStream.format("iceberg")
        .load(args.source)
        .writeStream.foreachBatch(make_batch_handler(args.target, tickers, clf))
        .option("checkpointLocation", args.checkpoint)
    )
    if args.once:
        writer = writer.trigger(availableNow=True)
    else:
        writer = writer.trigger(processingTime=f"{args.trigger_seconds} seconds")

    query = writer.start()
    print(f"scoring {args.source} -> {args.target}, checkpoint={args.checkpoint}")
    query.awaitTermination()
    if query.exception():
        print(f"job failed: {query.exception()}")
        return 1
    report(spark, args.target, args.model_version)
    print("job finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
