import io
import json
from datetime import UTC, datetime

import pytest

from ingestion.news.collector import NewsCollector, SeenCache, build_parser
from ingestion.news.event import NewsEvent
from ingestion.news.sinks import StdoutSink
from ingestion.news.sources import FetchError
from ingestion.news.tickers import DEFAULT_TICKERS_PATH, load_tickers

T = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


def _event(ticker, url):
    return NewsEvent.create(
        ticker=ticker,
        headline=f"news {url}",
        summary=None,
        source="fake",
        url=url,
        published_at=T,
        ingested_at=T,
    )


class FakeSource:
    name = "fake"

    def __init__(self, by_ticker, failing=()):
        self.by_ticker = by_ticker
        self.failing = set(failing)
        self.calls = []

    def fetch(self, ticker):
        self.calls.append(ticker)
        if ticker in self.failing:
            raise FetchError("boom")
        return list(self.by_ticker.get(ticker, []))


class ListSink:
    def __init__(self, fail_first=0):
        self.sent = []
        self.flushes = 0
        self.fail_first = fail_first

    def send(self, event):
        if self.fail_first:
            self.fail_first -= 1
            raise BufferError("queue full")
        self.sent.append(event)

    def flush(self):
        self.flushes += 1


def test_run_once_sends_all_events_and_waits_between_requests():
    source = FakeSource(
        {
            "AAPL": [_event("AAPL", "https://x.com/1")],
            "RKLB": [_event("RKLB", "https://x.com/2")],
        }
    )
    sink = ListSink()
    sleeps = []
    collector = NewsCollector(
        [source], sink, delay_between_requests=1.5, sleep=sleeps.append
    )

    stats = collector.run_once(["AAPL", "RKLB"])

    assert [e.ticker for e in sink.sent] == ["AAPL", "RKLB"]
    assert stats.sent == 2
    assert stats.per_ticker == {"AAPL": 1, "RKLB": 1}
    assert sleeps == [1.5]  # ไม่หน่วงก่อน request แรก
    assert sink.flushes == 1


def test_run_once_does_not_resend_seen_news_in_next_cycle():
    source = FakeSource({"AAPL": [_event("AAPL", "https://x.com/1")]})
    sink = ListSink()
    collector = NewsCollector([source], sink, delay_between_requests=0)

    collector.run_once(["AAPL"])
    stats = collector.run_once(["AAPL"])

    assert len(sink.sent) == 1
    assert stats.skipped_seen == 1


def test_same_article_for_two_tickers_is_sent_for_each():
    url = "https://x.com/shared"
    source = FakeSource({"AAPL": [_event("AAPL", url)], "MSFT": [_event("MSFT", url)]})
    sink = ListSink()

    NewsCollector([source], sink, delay_between_requests=0).run_once(["AAPL", "MSFT"])

    assert [e.ticker for e in sink.sent] == ["AAPL", "MSFT"]
    assert sink.sent[0].news_id == sink.sent[1].news_id


def test_failed_ticker_does_not_stop_others():
    source = FakeSource({"MSFT": [_event("MSFT", "https://x.com/1")]}, failing={"AAPL"})
    sink = ListSink()

    stats = NewsCollector([source], sink, delay_between_requests=0).run_once(
        ["AAPL", "MSFT"]
    )

    assert stats.failed_tickers == ["fake:AAPL"]
    assert len(sink.sent) == 1


def test_event_is_retried_next_cycle_if_send_failed():
    source = FakeSource({"AAPL": [_event("AAPL", "https://x.com/1")]})
    sink = ListSink(fail_first=1)
    collector = NewsCollector([source], sink, delay_between_requests=0)

    with pytest.raises(BufferError):
        collector.run_once(["AAPL"])
    collector.run_once(["AAPL"])

    assert len(sink.sent) == 1


def test_seen_cache_evicts_oldest():
    cache = SeenCache(max_size=2)
    for key in [("A", "1"), ("A", "2"), ("A", "3")]:
        cache.add(key)
    assert len(cache) == 2
    assert ("A", "1") not in cache
    assert ("A", "3") in cache


def test_stdout_sink_writes_json_lines():
    stream = io.StringIO()
    sink = StdoutSink(stream)
    sink.send(_event("AAPL", "https://x.com/1"))
    sink.flush()

    assert json.loads(stream.getvalue())["ticker"] == "AAPL"


@pytest.mark.parametrize("value", ["4", "16"])
def test_interval_must_be_5_to_15_minutes(value):
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--interval-min", value])


def test_repo_ticker_config_has_10_poc_tickers():
    tickers = load_tickers(DEFAULT_TICKERS_PATH)
    assert len(tickers) == 10
    assert "RKLB" in tickers


@pytest.mark.parametrize(
    "content",
    ["tickers: []", "tickers:\n  - ticker: aapl", "tickers:\n  - AAPL\n  - AAPL"],
)
def test_load_tickers_rejects_invalid_config(tmp_path, content):
    path = tmp_path / "tickers.yaml"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_tickers(path)


def test_kafka_sink_uses_ticker_as_key(monkeypatch):
    import sys
    import types

    produced = []

    class FakeProducer:
        def __init__(self, conf):
            self.conf = conf

        def produce(self, topic, key, value, on_delivery):
            produced.append((topic, key, json.loads(value)))

        def poll(self, timeout):
            return 0

        def flush(self, timeout):
            return 0

    monkeypatch.setitem(
        sys.modules, "confluent_kafka", types.SimpleNamespace(Producer=FakeProducer)
    )
    from ingestion.news.sinks import KafkaSink

    sink = KafkaSink("localhost:9092")
    sink.send(_event("RKLB", "https://x.com/1"))
    sink.flush()

    topic, key, value = produced[0]
    assert topic == "stock-news"
    assert key == b"RKLB"
    assert value["ticker"] == "RKLB"
