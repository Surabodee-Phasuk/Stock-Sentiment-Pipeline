import email.message
import urllib.error
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ingestion.news.sources import FetchError, YahooFinanceRss, parse_rss

FIXTURE = Path(__file__).parent / "fixtures" / "yahoo_rklb.xml"
NOW = datetime(2026, 10, 5, 15, 0, tzinfo=UTC)


def test_parse_rss_keeps_valid_items_only():
    events = parse_rss(
        FIXTURE.read_bytes(), ticker="RKLB", source="rss:yahoo", ingested_at=NOW
    )

    assert [e.headline for e in events] == [
        "Can Rocket Lab's Supply-Chain Strategy Support Future Growth?",
        "Is Rocket Lab Stock a Good Buy Right Now?",
    ]
    first, second = events
    assert first.ticker == "RKLB"
    assert first.source == "rss:yahoo"
    assert first.summary.startswith("RKLB strengthens")
    assert first.published_at == "2026-10-05T14:34:00Z"
    assert first.ingested_at == "2026-10-05T15:00:00Z"
    assert second.summary is None
    assert second.published_at == "2026-10-05T13:40:02Z"  # -0400 → UTC


def _http_error(code, retry_after=None):
    headers = email.message.Message()
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError("https://x", code, "err", headers, None)


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.urls = []

    def __call__(self, request, timeout):
        self.urls.append(request.full_url)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_fetch_builds_ticker_url_and_parses():
    opener = FakeOpener([FIXTURE.read_bytes()])
    source = YahooFinanceRss(opener=opener, sleep=lambda _: None, clock=lambda: NOW)

    events = source.fetch("RKLB")

    assert len(events) == 2
    assert "s=RKLB" in opener.urls[0]
    assert source.stats.requests == 1
    assert source.stats.status_counts == {200: 1}


def test_fetch_retries_on_rate_limit_using_retry_after():
    sleeps = []
    opener = FakeOpener([_http_error(429, retry_after=7), FIXTURE.read_bytes()])
    source = YahooFinanceRss(opener=opener, sleep=sleeps.append, clock=lambda: NOW)

    assert len(source.fetch("RKLB")) == 2
    assert sleeps == [7.0]
    assert source.stats.retries == 1
    assert source.stats.status_counts == {429: 1, 200: 1}


def test_fetch_uses_exponential_backoff_then_gives_up():
    sleeps = []
    opener = FakeOpener([urllib.error.URLError("down")] * 3)
    source = YahooFinanceRss(
        opener=opener,
        sleep=sleeps.append,
        max_retries=2,
        backoff_seconds=1.0,
        clock=lambda: NOW,
    )

    with pytest.raises(FetchError):
        source.fetch("RKLB")
    assert sleeps == [1.0, 2.0]
    assert source.stats.failures == 1


def test_fetch_does_not_retry_client_errors():
    opener = FakeOpener([_http_error(404)])
    source = YahooFinanceRss(
        opener=opener, sleep=lambda _: pytest.fail("should not sleep")
    )

    with pytest.raises(FetchError):
        source.fetch("NOPE")
    assert source.stats.requests == 1
