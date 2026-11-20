"""F2-05: สาธิต time travel และ schema evolution ของ Iceberg กับข่าวจริง (FR-2.5).

รันใน container `spark`:
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit lakehouse/demo/time_travel_schema_evolution.py [--keep]

ส่วน A อ่านอย่างเดียว: ย้อนดู `raw_news` จริง ณ snapshot แรกเทียบกับปัจจุบัน
ส่วน B ใช้ตารางสาธิต `zz_f205_demo` ที่คัดข่าวจาก `raw_news` มา (ไม่แตะตารางจริง)
    insert → delete → ย้อนดูทุกเวอร์ชัน → เพิ่ม/เปลี่ยนชื่อคอลัมน์โดยไม่เขียนไฟล์เก่าใหม่ → rollback
จบแล้วลบตารางสาธิตทิ้ง ใส่ `--keep` ถ้าจะเปิดดูต่อใน Athena (ดู `f2_05_athena.sql`)
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

DEFAULT_CATALOG = "glue"
DEFAULT_DATABASE = "stock_sentiment"
DEFAULT_SOURCE = "raw_news"
DEMO_TABLE = "zz_f205_demo"
FIRST_BATCH = 30
SECOND_BATCH = 10
DELETED_TICKER = "TSLA"


def demo_create_sql(table: str) -> str:
    return (
        f"CREATE TABLE {table} ("
        "news_id STRING, ticker STRING, headline STRING, source STRING, "
        "published_at TIMESTAMP) USING iceberg "
        "PARTITIONED BY (days(published_at)) "
        "TBLPROPERTIES ('format-version' = '2')"
    )


def sample_sql(source: str, limit: int, offset: int) -> str:
    """ข่าวไม่ซ้ำจาก raw เรียงตามเวลา ใช้ OFFSET แบ่งเป็นสองชุดที่ไม่ทับกัน."""
    return (
        "SELECT news_id, ticker, headline, source, published_at FROM ("
        "SELECT *, row_number() OVER (PARTITION BY news_id, ticker "
        "ORDER BY ingested_at) AS rn FROM "
        f"{source} WHERE news_id IS NOT NULL AND published_at IS NOT NULL"
        ") WHERE rn = 1 ORDER BY published_at, news_id, ticker "
        f"LIMIT {limit} OFFSET {offset}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Iceberg time travel demo (F2-05)")
    parser.add_argument("--catalog", default=DEFAULT_CATALOG)
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--keep", action="store_true", help="ไม่ลบตารางสาธิตตอนจบ")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("f2-05-time-travel-demo").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    sql = spark.sql
    source = f"{args.catalog}.{args.database}.{args.source}"
    demo = f"{args.catalog}.{args.database}.{DEMO_TABLE}"

    def title(text: str) -> None:
        print(f"\n===== {text} =====", flush=True)

    def count(query: str) -> int:
        return sql(query).first()[0]

    def columns(table_ref: str) -> list[str]:
        return sql(f"SELECT * FROM {table_ref} LIMIT 0").columns

    def snapshot_ids(table: str) -> list[int]:
        return [
            r[0]
            for r in sql(
                f"SELECT snapshot_id FROM {table}.snapshots ORDER BY committed_at"
            ).collect()
        ]

    def data_files(table: str) -> int:
        return count(f"SELECT count(*) FROM {table}.files")

    # ---------- ส่วน A: time travel กับตารางจริง (อ่านอย่างเดียว) ----------
    title(f"A. time travel กับตารางจริง {source} (อ่านอย่างเดียว)")
    sql(
        f"SELECT snapshot_id, date_format(committed_at, 'yyyy-MM-dd HH:mm:ss') "
        f"AS committed_at_utc, operation, summary['added-records'] AS added_rows "
        f"FROM {source}.snapshots ORDER BY committed_at"
    ).show(50, truncate=False)
    raw_snaps = snapshot_ids(source)
    if raw_snaps:
        first = raw_snaps[0]
        first_ts = sql(
            f"SELECT date_format(committed_at, 'yyyy-MM-dd HH:mm:ss.SSS') "
            f"FROM {source}.snapshots WHERE snapshot_id = {first}"
        ).first()[0]
        print(f"snapshots={len(raw_snaps)}")
        print(
            f"rows at first snapshot (VERSION AS OF {first}) = "
            f"{count(f'SELECT count(*) FROM {source} VERSION AS OF {first}')}"
        )
        print(
            f"rows at '{first_ts}' UTC (TIMESTAMP AS OF) = "
            f"{count(f'SELECT count(*) FROM {source} TIMESTAMP AS OF {chr(39)}{first_ts}{chr(39)}')}"
        )
        print(f"rows now = {count(f'SELECT count(*) FROM {source}')}")
    else:
        print("ยังไม่มี snapshot: รัน F2-02 ก่อน")
        return 1

    # ---------- ส่วน B: ตารางสาธิต ----------
    title(f"B1. สร้างตารางสาธิต {demo} และใส่ข่าวชุดแรก {FIRST_BATCH} ข่าว")
    sql(f"DROP TABLE IF EXISTS {demo} PURGE")
    sql(demo_create_sql(demo))
    sql(f"INSERT INTO {demo} {sample_sql(source, FIRST_BATCH, 0)}")
    print(f"rows={count(f'SELECT count(*) FROM {demo}')}")

    title(f"B2. เพิ่มข่าวชุดที่สอง {SECOND_BATCH} ข่าว")
    sql(f"INSERT INTO {demo} {sample_sql(source, SECOND_BATCH, FIRST_BATCH)}")
    print(f"rows={count(f'SELECT count(*) FROM {demo}')}")

    title(f"B3. ลบข่าวของ {DELETED_TICKER} (แก้ระดับแถว)")
    deleted = count(f"SELECT count(*) FROM {demo} WHERE ticker = '{DELETED_TICKER}'")
    sql(f"DELETE FROM {demo} WHERE ticker = '{DELETED_TICKER}'")
    print(
        f"deleted {DELETED_TICKER} rows={deleted} rows now={count(f'SELECT count(*) FROM {demo}')}"
    )

    title("B4. time travel: ย้อนดูทุกเวอร์ชัน")
    snaps = snapshot_ids(demo)
    sql(
        "SELECT snapshot_id, operation, summary['added-records'] AS added, "
        f"summary['deleted-records'] AS deleted FROM {demo}.snapshots "
        "ORDER BY committed_at"
    ).show(truncate=False)
    for i, sid in enumerate(snaps, start=1):
        total = count(f"SELECT count(*) FROM {demo} VERSION AS OF {sid}")
        tsla = count(
            f"SELECT count(*) FROM {demo} VERSION AS OF {sid} "
            f"WHERE ticker = '{DELETED_TICKER}'"
        )
        print(f"v{i} snapshot={sid}: rows={total} {DELETED_TICKER}={tsla}")

    title("B5. schema evolution: เพิ่มคอลัมน์และเปลี่ยนชื่อคอลัมน์")
    files_before = data_files(demo)
    snaps_before = len(snapshot_ids(demo))
    sql(f"ALTER TABLE {demo} ADD COLUMN sentiment_hint STRING")
    sql(f"ALTER TABLE {demo} RENAME COLUMN headline TO title")
    print(
        f"data files before={files_before} after={data_files(demo)} "
        f"snapshots before={snaps_before} after={len(snapshot_ids(demo))} "
        "(ไม่มีการเขียนไฟล์ข้อมูลใหม่)"
    )
    print(
        "old rows with sentiment_hint NULL = "
        f"{count(f'SELECT count(*) FROM {demo} WHERE sentiment_hint IS NULL')}"
    )
    sql(
        f"INSERT INTO {demo} SELECT news_id, ticker, headline, source, published_at, "
        f"'positive' FROM ({sample_sql(source, 3, FIRST_BATCH + SECOND_BATCH)})"
    )
    sql(
        f"SELECT ticker, title, sentiment_hint FROM {demo} "
        "ORDER BY sentiment_hint NULLS LAST, published_at DESC LIMIT 5"
    ).show(truncate=60)
    print(f"columns now        = {columns(demo)}")
    print(f"columns at v1      = {columns(f'{demo} VERSION AS OF {snaps[0]}')}")

    title("B6. rollback กลับไปเวอร์ชันก่อนลบ (v2)")
    sql(
        # ส่งชื่อเต็มรวม catalog ไม่อย่างนั้น Iceberg จะลองหา catalog ชื่อ database ก่อนแล้วพิมพ์ error ทิ้งไว้
        f"CALL {args.catalog}.system.rollback_to_snapshot('{demo}', {snaps[1]})"
    )
    print(
        f"rows={count(f'SELECT count(*) FROM {demo}')} "
        f"{DELETED_TICKER}={count(f'SELECT count(*) FROM {demo} WHERE ticker = {chr(39)}{DELETED_TICKER}{chr(39)}')} "
        f"(กลับมาเท่ากับ v2)"
    )

    if args.keep:
        print(f"\nkept {demo}: เปิดดูต่อใน Athena ด้วย lakehouse/demo/f2_05_athena.sql")
    else:
        sql(f"DROP TABLE {demo} PURGE")
        print(f"\ndropped {demo}")
    print("demo finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
