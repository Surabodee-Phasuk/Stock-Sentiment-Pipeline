"""News collector: ดึงข่าวของทุก ticker ทุก 5–15 นาที แล้วส่งเข้า Kafka `stock-news` (FR-1.1, FR-1.3).

รัน:
    python -m ingestion.news.collector --once --sink stdout     # ทดสอบโดยไม่ต้องมี Kafka
    python -m ingestion.news.collector                          # วนทุก 10 นาที ส่งเข้า Kafka
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from ingestion.news.sinks import DEFAULT_TOPIC, KafkaSink, NewsSink, StdoutSink
from ingestion.news.sources import FetchError, NewsSource, YahooFinanceRss
from ingestion.news.tickers import DEFAULT_TICKERS_PATH, load_tickers

log = logging.getLogger("ingestion.news")

MIN_INTERVAL_MINUTES = 5
MAX_INTERVAL_MINUTES = 15


@dataclass
class RunStats:
    fetched: int = 0
    sent: int = 0
    skipped_seen: int = 0
    failed_tickers: list[str] = field(default_factory=list)
    per_ticker: dict[str, int] = field(default_factory=dict)


class SeenCache:
    """จำ `(ticker, news_id)` ที่ส่งไปแล้วในโปรเซสนี้ เพื่อไม่ส่งข่าวเดิมซ้ำทุกรอบ.

    เป็นแค่การลด event ซ้ำที่ collector; การตัดซ้ำจริงทำที่ `clean_news` (MERGE on news_id, F2-03)
    """

    def __init__(self, max_size: int = 50_000) -> None:
        self._max_size = max_size
        self._keys: OrderedDict[tuple[str, str], None] = OrderedDict()

    def __contains__(self, key: tuple[str, str]) -> bool:
        if key in self._keys:
            self._keys.move_to_end(key)
            return True
        return False

    def add(self, key: tuple[str, str]) -> None:
        self._keys[key] = None
        self._keys.move_to_end(key)
        if len(self._keys) > self._max_size:
            self._keys.popitem(last=False)

    def __len__(self) -> int:
        return len(self._keys)


class NewsCollector:
    def __init__(
        self,
        sources: Sequence[NewsSource],
        sink: NewsSink,
        *,
        delay_between_requests: float = 1.0,
        seen: SeenCache | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.sources = list(sources)
        self.sink = sink
        self.delay_between_requests = delay_between_requests
        self.seen = seen if seen is not None else SeenCache()
        self._sleep = sleep

    def run_once(self, tickers: Sequence[str]) -> RunStats:
        stats = RunStats()
        first_request = True
        for ticker in tickers:
            stats.per_ticker.setdefault(ticker, 0)
            for source in self.sources:
                if not first_request and self.delay_between_requests > 0:
                    # เว้นจังหวะระหว่าง request เพื่อไม่ชน rate limit ของแหล่งข่าว
                    self._sleep(self.delay_between_requests)
                first_request = False
                try:
                    events = source.fetch(ticker)
                except FetchError as exc:
                    log.error(
                        "source=%s ticker=%s failed: %s", source.name, ticker, exc
                    )
                    stats.failed_tickers.append(f"{source.name}:{ticker}")
                    continue

                stats.fetched += len(events)
                stats.per_ticker[ticker] += len(events)
                for event in events:
                    key = (event.ticker, event.news_id)
                    if key in self.seen:
                        stats.skipped_seen += 1
                        continue
                    self.sink.send(event)
                    # จำหลังส่งสำเร็จเท่านั้น ถ้า send ล้ม รอบถัดไปจะส่งใหม่
                    self.seen.add(key)
                    stats.sent += 1
        self.sink.flush()
        return stats


def run_forever(
    collector: NewsCollector,
    tickers: Sequence[str],
    interval_seconds: float,
    stop: threading.Event,
) -> None:
    while not stop.is_set():
        started = time.monotonic()
        try:
            stats = collector.run_once(tickers)
        except Exception:
            # รอบที่ล้ม (เช่น Kafka ไม่ตอบ) ไม่ควรหยุด collector ทั้งตัว รอบถัดไปลองใหม่
            log.exception("cycle failed")
            stop.wait(max(0.0, interval_seconds - (time.monotonic() - started)))
            continue
        elapsed = time.monotonic() - started
        log.info(
            "cycle done in %.1fs: fetched=%d sent=%d skipped_seen=%d failed=%s per_ticker=%s",
            elapsed,
            stats.fetched,
            stats.sent,
            stats.skipped_seen,
            stats.failed_tickers or "-",
            stats.per_ticker,
        )
        stop.wait(max(0.0, interval_seconds - elapsed))


def _interval_minutes(value: str) -> float:
    minutes = float(value)
    if not MIN_INTERVAL_MINUTES <= minutes <= MAX_INTERVAL_MINUTES:
        raise argparse.ArgumentTypeError(
            f"interval must be {MIN_INTERVAL_MINUTES}-{MAX_INTERVAL_MINUTES} minutes (FR-1.1)"
        )
    return minutes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect stock news and publish to Kafka"
    )
    parser.add_argument("--tickers-file", type=Path, default=DEFAULT_TICKERS_PATH)
    parser.add_argument("--interval-min", type=_interval_minutes, default=10.0)
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument("--sink", choices=["kafka", "stdout"], default="kafka")
    parser.add_argument(
        "--bootstrap-servers",
        default=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    )
    parser.add_argument(
        "--topic", default=os.environ.get("KAFKA_NEWS_TOPIC", DEFAULT_TOPIC)
    )
    parser.add_argument(
        "--delay", type=float, default=1.0, help="seconds between source requests"
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
    sink: NewsSink = (
        StdoutSink()
        if args.sink == "stdout"
        else KafkaSink(args.bootstrap_servers, args.topic)
    )
    source = YahooFinanceRss()
    collector = NewsCollector([source], sink, delay_between_requests=args.delay)
    log.info("collecting %d tickers: %s", len(tickers), ", ".join(tickers))

    if args.once:
        stats = collector.run_once(tickers)
        log.info(
            "fetched=%d sent=%d failed=%s per_ticker=%s source_stats=%s",
            stats.fetched,
            stats.sent,
            stats.failed_tickers or "-",
            stats.per_ticker,
            source.stats,
        )
        return 1 if stats.failed_tickers else 0

    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    run_forever(collector, tickers, args.interval_min * 60, stop)
    log.info("stopped; source_stats=%s", source.stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
