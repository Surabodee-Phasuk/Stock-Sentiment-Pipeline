"""Daily close collector: ดึงราคาปิดของทุก ticker วันละครั้ง แล้วเขียน JSON Lines ให้ Spark batch อ่าน (FR-1.2, F2-04).

รัน:
    python -m ingestion.price.collector --sink stdout      # ทดสอบ พิมพ์ออกจอ
    python -m ingestion.price.collector                    # เขียน data/price/daily_close_<วันที่>.jsonl

ดึงย้อนหลังหลายวัน (`--days`, ค่าเริ่ม 7) ทุกครั้ง ถ้าวันไหนลืมรันจะได้ราคาวันนั้นในรอบถัดไป
แถวซ้ำข้ามไฟล์ไม่เป็นปัญหา เพราะ `daily_price` MERGE on `ticker, trade_date` (F2-04)
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from ingestion.news.sources import FetchError
from ingestion.news.tickers import DEFAULT_TICKERS_PATH, load_tickers
from ingestion.price.sources import DailyClose, YahooChart

log = logging.getLogger("ingestion.price")

DEFAULT_OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "price"
MIN_DAYS = 1
MAX_DAYS = 30


@dataclass
class RunStats:
    rows: list[DailyClose] = field(default_factory=list)
    failed_tickers: list[str] = field(default_factory=list)
    per_ticker: dict[str, int] = field(default_factory=dict)
    latest_date: dict[str, str] = field(default_factory=dict)


def collect(
    source: YahooChart,
    tickers: Sequence[str],
    *,
    days: int,
    delay_between_tickers: float = 2.0,
    sleep: Callable[[float], None] = time.sleep,
) -> RunStats:
    stats = RunStats()
    for i, ticker in enumerate(tickers):
        if i > 0 and delay_between_tickers > 0:
            # เว้นจังหวะระหว่างหุ้น ลดโอกาสโดน Yahoo บล็อก (docs/09)
            sleep(delay_between_tickers)
        try:
            rows = source.fetch(ticker, days)
        except FetchError as exc:
            log.error("ticker=%s failed: %s", ticker, exc)
            stats.failed_tickers.append(ticker)
            continue
        if not rows:
            log.error("ticker=%s returned no closed trading day", ticker)
            stats.failed_tickers.append(ticker)
            continue
        stats.rows.extend(rows)
        stats.per_ticker[ticker] = len(rows)
        stats.latest_date[ticker] = rows[-1].trade_date
    return stats


def write_jsonl(rows: Sequence[DailyClose], path: Path) -> None:
    """เขียนทับไฟล์เดิมของวันเดียวกัน รันซ้ำในวันเดียวกันจึงไม่ได้ไฟล์เพิ่ม."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("".join(row.to_json() + "\n" for row in rows), encoding="utf-8")
    tmp.replace(path)


def _days(value: str) -> int:
    days = int(value)
    if not MIN_DAYS <= days <= MAX_DAYS:
        raise argparse.ArgumentTypeError(
            f"days must be {MIN_DAYS}-{MAX_DAYS} (ย้อนหลังนานกว่านี้ใช้ backfill F1-04)"
        )
    return days


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect daily close prices")
    parser.add_argument("--tickers-file", type=Path, default=DEFAULT_TICKERS_PATH)
    parser.add_argument(
        "--days", type=_days, default=7, help="calendar days to look back"
    )
    parser.add_argument("--sink", choices=["file", "stdout"], default="file")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--delay", type=float, default=2.0, help="seconds between tickers"
    )
    parser.add_argument("--log-level", default="INFO")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    tickers = load_tickers(args.tickers_file)
    source = YahooChart()
    log.info(
        "collecting daily close for %d tickers, last %d days", len(tickers), args.days
    )
    stats = collect(source, tickers, days=args.days, delay_between_tickers=args.delay)

    if args.sink == "stdout":
        for row in stats.rows:
            sys.stdout.write(row.to_json() + "\n")
        sys.stdout.flush()
    elif stats.rows:
        run_date = datetime.now(UTC).date().isoformat()
        path = args.out_dir / f"daily_close_{run_date}.jsonl"
        write_jsonl(stats.rows, path)
        log.info("wrote %d rows to %s", len(stats.rows), path)

    log.info(
        "rows=%d failed=%s per_ticker=%s latest=%s source_stats=%s",
        len(stats.rows),
        stats.failed_tickers or "-",
        stats.per_ticker,
        stats.latest_date,
        source.stats,
    )
    return 1 if stats.failed_tickers else 0


if __name__ == "__main__":
    raise SystemExit(main())
