"""แหล่งข่าว: แต่ละ source ดึงข่าวของ ticker หนึ่งตัวและคืน `NewsEvent`.

PoC เริ่มที่ Yahoo Finance RSS (ไม่ต้องใช้ API key, มี feed แยกต่อ ticker)
แหล่งอื่นและการตัดซ้ำข้ามแหล่งอยู่ใน F1-03
"""

from __future__ import annotations

import logging
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Protocol
from urllib.parse import quote

from ingestion.news.event import NewsEvent

log = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; StockSentimentPipeline/0.1; +capstone project)"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class NewsSource(Protocol):
    name: str

    def fetch(self, ticker: str) -> list[NewsEvent]: ...


class FetchError(RuntimeError):
    pass


@dataclass
class SourceStats:
    """ตัวเลขสำหรับบันทึก rate limit จริงใน Evidence."""

    requests: int = 0
    retries: int = 0
    failures: int = 0
    status_counts: dict[int, int] = field(default_factory=dict)

    def record_status(self, status: int) -> None:
        self.status_counts[status] = self.status_counts.get(status, 0) + 1


def parse_rss(
    xml_bytes: bytes,
    *,
    ticker: str,
    source: str,
    ingested_at: datetime,
) -> list[NewsEvent]:
    """แปลง RSS 2.0 เป็น `NewsEvent` ข้าม item ที่ไม่มี title/link/pubDate ที่ใช้ได้."""
    root = ET.fromstring(xml_bytes)
    events: list[NewsEvent] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        if not title or not link or not pub_date:
            log.debug("skip item without title/link/pubDate: %r", title or link)
            continue
        try:
            published_at = parsedate_to_datetime(pub_date)
        except (TypeError, ValueError):
            log.debug("skip item with bad pubDate %r", pub_date)
            continue
        if published_at.tzinfo is None:
            # RFC 822 ที่ไม่มี zone ถือเป็น UTC
            published_at = published_at.replace(tzinfo=UTC)
        try:
            events.append(
                NewsEvent.create(
                    ticker=ticker,
                    headline=title,
                    summary=item.findtext("description"),
                    source=source,
                    url=link,
                    published_at=published_at,
                    ingested_at=ingested_at,
                )
            )
        except ValueError as exc:
            log.debug("skip invalid item %r: %s", link, exc)
    return events


class YahooFinanceRss:
    """Yahoo Finance headline RSS ต่อ ticker."""

    name = "rss:yahoo"
    url_template = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"

    def __init__(
        self,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff_seconds: float = 2.0,
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

    def fetch(self, ticker: str) -> list[NewsEvent]:
        url = self.url_template.format(ticker=quote(ticker))
        body = self._get_with_retry(url)
        return parse_rss(
            body, ticker=ticker, source=self.name, ingested_at=self._clock()
        )

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
                retry_after = _retry_after_seconds(exc)
                error: Exception = exc
            except (urllib.error.URLError, TimeoutError) as exc:
                retry_after = None
                error = exc

            if attempt == self.max_retries:
                self.stats.failures += 1
                raise FetchError(f"{url}: {error}") from error
            delay = (
                retry_after
                if retry_after is not None
                else self.backoff_seconds * 2**attempt
            )
            self.stats.retries += 1
            log.warning("fetch %s failed (%s), retry in %.1fs", url, error, delay)
            self._sleep(delay)
        raise AssertionError("unreachable")


def _http_get(request: urllib.request.Request, timeout: float) -> bytes:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    value = exc.headers.get("Retry-After") if exc.headers else None
    if value and value.isdigit():
        return min(float(value), 300.0)
    return None
