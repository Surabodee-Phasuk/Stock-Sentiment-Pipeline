"""ขั้นตอนร่วมของ F3-01 (streaming) และ F3-04 (reprocess): ข่าว → FinBERT → `news_sentiment`.

ทั้งสองงานใช้ฟังก์ชันชุดนี้ ผลจึงเหมือนกันไม่ว่าจะมาจาก streaming หรือ reprocess:
1. `valid_unique_news`  ตรวจข่าวด้วยกฎเดียวกับ F2-03 แล้วเก็บแถวแรกของแต่ละ (news_id, ticker)
2. `pending_news`       ตัดคีย์ที่มีผลของ model_version นี้แล้ว (ไม่เรียกโมเดลซ้ำ)
3. `score_rows`         เรียก FinBERT เป็นชุดบน driver (ข่าว ~300 ชิ้นต่อรอบใน PoC)
4. `write_scores`       MERGE ด้วยคีย์ (news_id, ticker, model_version) แบบเพิ่มเฉพาะที่ยังไม่มี
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from sentiment.finbert import FinBertClassifier, build_text

# คอลัมน์ตามลำดับใน lakehouse/ddl/04_news_sentiment.sql
SENTIMENT_COLUMNS = (
    "news_id",
    "ticker",
    "published_at",
    "sentiment",
    "sentiment_score",
    "model_name",
    "model_version",
    "processed_at",
)
SENTIMENT_SCHEMA = (
    "news_id STRING, ticker STRING, published_at TIMESTAMP, sentiment STRING, "
    "sentiment_score DOUBLE, model_name STRING, model_version STRING, "
    "processed_at TIMESTAMP"
)
INPUT_COLUMNS = ("news_id", "ticker", "published_at", "headline", "summary")


def merge_sql(target: str, updates_view: str) -> str:
    return (
        f"MERGE INTO {target} t USING {updates_view} s "
        "ON t.news_id = s.news_id AND t.ticker = s.ticker "
        "AND t.model_version = s.model_version "
        "WHEN NOT MATCHED THEN INSERT *"
    )


def score_rows(
    rows: Iterable[Mapping[str, Any]],
    clf: FinBertClassifier,
    processed_at: datetime | None = None,
) -> list[tuple]:
    """ข่าว (dict ที่มี INPUT_COLUMNS) → tuple ตาม SENTIMENT_COLUMNS."""
    rows = list(rows)
    preds = clf.predict([build_text(r["headline"], r.get("summary")) for r in rows])
    when = processed_at or datetime.now(timezone.utc).replace(tzinfo=None)
    return [
        (
            r["news_id"],
            r["ticker"],
            r["published_at"],
            p.sentiment,
            p.score,
            clf.model_name,
            clf.model_version,
            when,
        )
        for r, p in zip(rows, preds, strict=True)
    ]


def valid_unique_news(df, tickers: Sequence[str]):
    """กฎตรวจเดียวกับ clean_news (F2-03) แล้วเก็บแถวแรกที่เจอของแต่ละ (news_id, ticker)."""
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    from streaming.clean_news_job import reject_reason_sql

    if "loaded_at" not in df.columns:  # clean_news ไม่มี loaded_at ใช้ ingested_at แทน
        df = df.withColumn("loaded_at", F.col("ingested_at"))
    order = [F.col("ingested_at").asc_nulls_last()]
    if "kafka_offset" in df.columns:
        order.append(F.col("kafka_offset").asc_nulls_last())
    first_seen = Window.partitionBy("news_id", "ticker").orderBy(*order)
    return (
        df.where(F.expr(reject_reason_sql(tickers)).isNull())
        .withColumn("_rn", F.row_number().over(first_seen))
        .where("_rn = 1")
        .select(*INPUT_COLUMNS)
    )


def pending_news(news_df, target: str, model_version: str):
    """ข่าวที่ยังไม่มีผลของ model_version นี้ใน target."""
    spark = news_df.sparkSession
    done = (
        spark.table(target)
        .where(f"model_version = '{model_version}'")
        .select("news_id", "ticker")
    )
    return news_df.join(done, ["news_id", "ticker"], "left_anti")


def write_scores(spark, scored: Sequence[tuple], target: str) -> int:
    """MERGE ผลลง target คืนจำนวนแถวที่เพิ่มจริง."""
    if not scored:
        return 0
    updates = spark.createDataFrame(list(scored), SENTIMENT_SCHEMA)
    before = spark.table(target).count()
    updates.createOrReplaceTempView("news_sentiment_updates")
    spark.sql(merge_sql(target, "news_sentiment_updates"))
    return spark.table(target).count() - before


def score_and_write(news_df, target: str, clf: FinBertClassifier) -> dict[str, float]:
    """ขั้น 2–4 รวมกัน คืนตัวเลขไว้พิมพ์ log."""
    import time

    spark = news_df.sparkSession
    todo = [
        r.asDict() for r in pending_news(news_df, target, clf.model_version).collect()
    ]
    started = time.perf_counter()
    scored = score_rows(todo, clf)
    infer_s = time.perf_counter() - started
    inserted = write_scores(spark, scored, target)
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for row in scored:
        counts[row[3]] += 1
    return {
        "scored": len(scored),
        "inserted": inserted,
        "infer_seconds": round(infer_s, 2),
        "news_per_second": round(len(scored) / infer_s, 1) if scored and infer_s else 0,
        **counts,
    }
