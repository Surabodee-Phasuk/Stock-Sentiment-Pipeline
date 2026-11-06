"""F2-02: เช็กข้อมูลใน `raw_news` และวัดเวลาตั้งแต่ข่าวออกจนลงตาราง (เกณฑ์ไม่เกิน 15 นาที).

รันใน container `spark`:
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit streaming/check_raw_news.py

"ข่าวใหม่" คือข่าวที่เจอครั้งแรกในรอบดึงที่ห่างจากรอบก่อนไม่เกิน 15 นาที (collector รันต่อเนื่อง)
ไม่นับรอบแรกของแต่ละครั้งที่เปิด collector เพราะรอบนั้นดึงข่าวเก่าที่ค้างใน feed ซึ่งบอกไม่ได้ว่า pipeline เร็วแค่ไหน
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

DEFAULT_TABLE = "glue.stock_sentiment.raw_news"
MAX_LATENCY_SECONDS = 15 * 60
# รอบดึงหนึ่งรอบ request ห่างกันไม่กี่วินาที ส่วน collector เว้นรอบอย่างน้อย 5 นาที
ROUND_GAP_SECONDS = 2 * 60


@dataclass(frozen=True)
class NewsRow:
    news_id: str
    ticker: str
    published_at: int
    ingested_at: int
    loaded_at: int


def find_rounds(ingested_times: Iterable[int]) -> list[tuple[int, int]]:
    """รวมเวลา `ingested_at` เป็นรอบดึง `(เริ่ม, จบ)` เรียงตามเวลา."""
    rounds: list[tuple[int, int]] = []
    for ts in sorted(set(ingested_times)):
        if rounds and ts - rounds[-1][1] <= ROUND_GAP_SECONDS:
            rounds[-1] = (rounds[-1][0], ts)
        else:
            rounds.append((ts, ts))
    return rounds


def fresh_news(rows: Iterable[NewsRow]) -> list[NewsRow]:
    """คืนแถวแรกของข่าวที่เจอครั้งแรกระหว่างที่ collector รันต่อเนื่อง."""
    rows = list(rows)
    rounds = find_rounds(row.ingested_at for row in rows)
    starts = [start for start, _ in rounds]

    first_seen: dict[tuple[str, str], NewsRow] = {}
    for row in rows:
        key = (row.news_id, row.ticker)
        if key not in first_seen or row.ingested_at < first_seen[key].ingested_at:
            first_seen[key] = row

    fresh = []
    for row in first_seen.values():
        i = bisect_right(starts, row.ingested_at) - 1
        if i > 0 and rounds[i][0] - rounds[i - 1][1] <= MAX_LATENCY_SECONDS:
            fresh.append(row)
    return fresh


def percentile(values: Sequence[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[min(int(len(ordered) * fraction), len(ordered) - 1)]


def describe(values: Sequence[int]) -> str:
    within = sum(1 for v in values if v <= MAX_LATENCY_SECONDS)
    return (
        f"p50={percentile(values, 0.5)}s p95={percentile(values, 0.95)}s "
        f"max={max(values)}s within_15min={within}/{len(values)}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check raw_news and latency")
    parser.add_argument("--table", default=DEFAULT_TABLE)
    args = parser.parse_args(argv)

    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F

    spark = SparkSession.builder.appName("f2-02-check-raw-news").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    df = spark.table(args.table).cache()

    total = df.count()
    print(f"rows={total} table={args.table}")
    if total == 0:
        print("no rows yet")
        return 1

    news = df.where(
        "news_id IS NOT NULL AND published_at IS NOT NULL AND ingested_at IS NOT NULL"
    )
    print(f"unreadable_rows={total - news.count()} (เก็บไว้ใน Raw, F2-03 กรองออก)")
    print(
        "unique (news_id, ticker)="
        f"{news.select('news_id', 'ticker').distinct().count()}"
    )
    news.groupBy("source").count().orderBy("source").show(truncate=False)
    news.groupBy("ticker").count().orderBy("ticker").show(50, truncate=False)

    rows = [
        NewsRow(r["news_id"], r["ticker"], r["p"], r["i"], r["l"])
        for r in news.select(
            "news_id",
            "ticker",
            F.col("published_at").cast("long").alias("p"),
            F.col("ingested_at").cast("long").alias("i"),
            F.col("loaded_at").cast("long").alias("l"),
        ).collect()
    ]
    print(f"collector rounds={len(find_rounds(r.ingested_at for r in rows))}")

    fresh = fresh_news(rows)
    if not fresh:
        print("no fresh news yet: ให้ collector รันต่อเนื่องหลายรอบแล้วเช็กใหม่")
        return 0
    print(f"fresh news={len(fresh)}")
    print(
        "collector->table (pipeline): "
        + describe([r.loaded_at - r.ingested_at for r in fresh])
    )
    print(
        "published->collector (feed): "
        + describe([r.ingested_at - r.published_at for r in fresh])
    )
    print(
        "published->table (รวม):      "
        + describe([r.loaded_at - r.published_at for r in fresh])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
