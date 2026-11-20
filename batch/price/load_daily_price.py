"""F2-04: Spark batch โหลดราคาปิดจาก F1-02 ลง `raw_daily_price` แล้ว MERGE เข้า `daily_price` (FR-2.4).

รันใน container `spark` หลังรัน collector ราคา (`python -m ingestion.price.collector`):
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit batch/price/load_daily_price.py

ขั้นตอน
1. อ่านไฟล์ `data/price/daily_close_*.jsonl` (schema "Daily close (batch)" ใน docs/05)
2. append ทุกแถวลง `raw_daily_price` ตามที่รับมา (Raw ไม่แก้ไม่ลบ)
3. ตัดแถวที่ไม่ผ่านการตรวจ แล้วเลือกแถวล่าสุด (`ingested_at` มากสุด) ต่อ (ticker, trade_date)
4. MERGE เข้า `daily_price` ด้วยคีย์ (ticker, trade_date): ยังไม่มีให้เพิ่ม มีแล้วอัปเดตเมื่อข้อมูลใหม่กว่า

`daily_price` รันซ้ำได้โดยไม่เกิดแถวซ้ำ ส่วน `raw_daily_price` จะมีแถวเพิ่มทุกครั้งที่โหลด (เป็นบันทึกการโหลด)
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = str(ROOT / "data" / "price" / "daily_close_*.jsonl")
DEFAULT_RAW = "glue.stock_sentiment.raw_daily_price"
DEFAULT_TARGET = "glue.stock_sentiment.daily_price"
TICKERS_FILE = ROOT / "config" / "tickers.yaml"
# คอลัมน์ตามลำดับใน lakehouse/ddl/02_raw_daily_price.sql และ 05_daily_price.sql
RAW_COLUMNS = ("ticker", "trade_date", "close", "source", "ingested_at", "loaded_at")
PRICE_COLUMNS = ("ticker", "trade_date", "close", "source", "ingested_at", "updated_at")
EARLIEST_TRADE_DATE = "2000-01-01"
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
        "WHEN ticker IS NULL OR trade_date IS NULL OR ingested_at IS NULL "
        "THEN 'missing_field' "
        "WHEN close IS NULL OR isnan(close) OR close <= 0 THEN 'bad_close' "
        f"WHEN trade_date < DATE '{EARLIEST_TRADE_DATE}' "
        "OR trade_date > current_date() THEN 'bad_trade_date' "
        f"WHEN ticker NOT IN ({allowed}) THEN 'unknown_ticker' "
        "END"
    )


def merge_sql(target: str, updates_view: str) -> str:
    return (
        f"MERGE INTO {target} t USING {updates_view} s "
        "ON t.ticker = s.ticker AND t.trade_date = s.trade_date "
        "WHEN MATCHED AND s.ingested_at > t.ingested_at THEN UPDATE SET "
        "t.close = s.close, t.source = s.source, "
        "t.ingested_at = s.ingested_at, t.updated_at = s.updated_at "
        "WHEN NOT MATCHED THEN INSERT *"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="daily close files -> Iceberg")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="path หรือ glob")
    parser.add_argument("--raw-table", default=DEFAULT_RAW)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--tickers-file", type=Path, default=TICKERS_FILE)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tickers = load_tickers(args.tickers_file)

    from pyspark.sql import SparkSession, Window
    from pyspark.sql import functions as F
    from pyspark.sql.types import DoubleType, StringType, StructField, StructType

    spark = SparkSession.builder.appName("f2-04-load-daily-price").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    schema = StructType(
        [
            StructField("ticker", StringType()),
            StructField("trade_date", StringType()),
            StructField("close", DoubleType()),
            StructField("source", StringType()),
            StructField("ingested_at", StringType()),
        ]
    )
    files = spark.read.schema(schema).json(args.input)
    # try_cast / try_to_timestamp: Spark 4 เปิด ANSI ไว้ ถ้าแปลงแบบปกติ แถวที่รูปแบบผิดจะทำให้ทั้ง job ล้ม
    loaded = (
        files.select(
            F.upper(F.trim("ticker")).alias("ticker"),
            F.expr("try_cast(trade_date AS DATE)").alias("trade_date"),
            F.col("close"),
            F.col("source"),
            F.expr("try_to_timestamp(ingested_at)").alias("ingested_at"),
            F.current_timestamp().alias("loaded_at"),
        )
        .select(*RAW_COLUMNS)
        .cache()
    )
    file_rows = loaded.count()
    print(f"input={args.input} rows={file_rows}")
    if file_rows == 0:
        print("no rows: รัน python -m ingestion.price.collector ก่อน")
        return 1

    loaded.writeTo(args.raw_table).append()
    print(f"appended {file_rows} rows to {args.raw_table}")

    tagged = loaded.withColumn("reject_reason", F.expr(reject_reason_sql(tickers)))
    rejected = {
        r["reject_reason"]: r["count"]
        for r in tagged.where("reject_reason IS NOT NULL")
        .groupBy("reject_reason")
        .count()
        .collect()
    }
    latest = Window.partitionBy("ticker", "trade_date").orderBy(
        F.col("ingested_at").desc()
    )
    updates = (
        tagged.where("reject_reason IS NULL")
        .withColumn("_rn", F.row_number().over(latest))
        .where("_rn = 1")
        .withColumn("updated_at", F.current_timestamp())
        .select(*PRICE_COLUMNS)
    )
    keys = updates.count()

    before = spark.table(args.target).count()
    updates.createOrReplaceTempView("daily_price_updates")
    spark.sql(merge_sql(args.target, "daily_price_updates"))
    after = spark.table(args.target).count()

    row = spark.sql(
        "SELECT count(*) AS n, count(DISTINCT ticker, trade_date) AS k, "
        f"count(DISTINCT ticker) AS tickers, max(trade_date) AS latest FROM {args.target}"
    ).first()
    print(
        f"rejected={rejected or 0} unique_keys={keys} inserted={after - before} "
        f"(ที่เหลือเป็นแถวเดิมที่อัปเดตหรือข้าม)"
    )
    print(
        f"daily_price rows={row['n']} unique (ticker, trade_date)={row['k']} "
        f"duplicates={row['n'] - row['k']} tickers={row['tickers']} "
        f"latest={row['latest']}"
    )
    print("load finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
