"""ราคาปิดรายวันจาก Yahoo Finance chart API (endpoint เดียวกับที่ yfinance ใช้).

เรียก endpoint ตรงด้วย urllib แทนการลง yfinance เพื่อไม่ต้องพึ่ง pandas และทดสอบด้วย fixture ได้
Yahoo ไม่มี API ทางการ จึงดึงวันละครั้ง เว้นจังหวะระหว่างหุ้น และ retry เมื่อโดนบล็อกชั่วคราว (docs/09)
"""

from __future__ import annotations

import json
import logging
import math
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from urllib.parse import quote

from ingestion.news.event import to_utc_iso
from ingestion.news.sources import (
    RETRYABLE_STATUS,
    USER_AGENT,
    FetchError,
    SourceStats,
)

log = logging.getLogger(__name__)

SOURCE = "yahoo_finance"


@dataclass(frozen=True, slots=True)
class DailyClose:
    """ราคาปิดหนึ่งวันของหนึ่งหุ้น ตาม schema "Daily close (batch)" ใน docs/05."""

    ticker: str
    trade_date: str
    close: float
    source: str
    ingested_at: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))


def parse_chart(
    body: bytes,
    *,
    ticker: str,
    now: datetime,
    ingested_at: datetime,
) -> list[DailyClose]:
    """แปลงผล chart API (interval=1d) เป็นราคาปิดรายวัน เรียงตาม `trade_date`.

    - `trade_date` คือวันตามเวลาตลาด (ใช้ `gmtoffset` ของตลาด) ไม่ใช่วันตาม UTC
    - ข้ามแท่งของวันที่ตลาดยังไม่ปิด เพราะราคานั้นยังไม่ใช่ราคาปิด
    - ข้ามวันที่ไม่มีราคา (Yahoo ส่ง `null` มาในบางวัน)
    """
    chart = json.loads(body).get("chart") or {}
    if chart.get("error"):
        raise ValueError(f"chart error: {chart['error']}")
    results = chart.get("result") or []
    if not results:
        raise ValueError("chart has no result")
    result = results[0]

    meta = result.get("meta") or {}
    symbol = (meta.get("symbol") or ticker).upper()
    if symbol != ticker.upper():
        raise ValueError(f"asked for {ticker} but got {symbol}")
    gmtoffset = int(meta.get("gmtoffset") or 0)
    regular = (meta.get("currentTradingPeriod") or {}).get("regular") or {}
    session_start = regular.get("start")
    session_end = regular.get("end")

    timestamps = result.get("timestamp") or []
    quotes = (result.get("indicators") or {}).get("quote") or [{}]
    closes = quotes[0].get("close") or []

    by_date: dict[date, float] = {}
    for ts, close in zip(timestamps, closes, strict=False):
        if close is None or not math.isfinite(close) or close <= 0:
            log.debug("%s: skip bar %s without close", ticker, ts)
            continue
        if (
            session_start is not None
            and session_end is not None
            and ts >= session_start
            and now.timestamp() < session_end
        ):
            log.debug("%s: skip bar %s, session not closed yet", ticker, ts)
            continue
        trade_date = datetime.fromtimestamp(ts, UTC) + timedelta(seconds=gmtoffset)
        # ค่าจาก Yahoo เป็น float ที่มีเศษ เช่น 64.22000122070312
        by_date[trade_date.date()] = round(close, 4)

    stamp = to_utc_iso(ingested_at)
    return [
        DailyClose(
            ticker=ticker.upper(),
            trade_date=day.isoformat(),
            close=close,
            source=SOURCE,
            ingested_at=stamp,
        )
        for day, close in sorted(by_date.items())
    ]


class YahooChart:
    """ราคาปิดรายวันย้อนหลัง `days` วันปฏิทินของ ticker หนึ่งตัว."""

    url_template = (
        "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        "?interval=1d&period1={start}&period2={end}&events=history"
    )

    def __init__(
        self,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff_seconds: float = 5.0,
        opener: Callable[[urllib.request.Request, float], bytes] | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self._open = opener or _http_get
        self._sleep = sleep
        self._clock = clock
        self.stats = SourceStats()

    def fetch(self, ticker: str, days: int) -> list[DailyClose]:
        now = self._clock()
        url = self.url_template.format(
            ticker=quote(ticker),
            start=int((now - timedelta(days=days)).timestamp()),
            end=int(now.timestamp()),
        )
        body = self._get_with_retry(url)
        try:
            return parse_chart(body, ticker=ticker, now=now, ingested_at=now)
        except (ValueError, KeyError, TypeError) as exc:
            self.stats.failures += 1
            raise FetchError(f"{ticker}: {exc}") from exc

    def _get_with_retry(self, url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        for attempt in range(self.max_retries + 1):
            self.stats.requests += 1
            try:
                body = self._open(request, self.timeout)
                self.stats.record_status(200)
                return body
            except urllib.error.HTTPError as exc:
                self.stats.record_status(exc.code)
                if exc.code not in RETRYABLE_STATUS:
                    self.stats.failures += 1
                    raise FetchError(f"{url}: HTTP {exc.code}") from exc
                error: Exception = exc
            except (urllib.error.URLError, TimeoutError) as exc:
                error = exc

            if attempt == self.max_retries:
                self.stats.failures += 1
                raise FetchError(f"{url}: {error}") from error
            delay = self.backoff_seconds * 2**attempt
            self.stats.retries += 1
            log.warning("fetch %s failed (%s), retry in %.1fs", url, error, delay)
            self._sleep(delay)
        raise AssertionError("unreachable")


def _http_get(request: urllib.request.Request, timeout: float) -> bytes:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()
