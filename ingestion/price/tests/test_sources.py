import email.message
import json
import urllib.error
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ingestion.news.sources import FetchError
from ingestion.price.sources import YahooChart, parse_chart

FIXTURE = Path(__file__).parent / "fixtures" / "yahoo_chart_rklb.json"
# 2026-10-20 03:00 UTC = 19 ต.ค. 23:00 ที่นิวยอร์ก หลังตลาดปิด ก่อนรอบ 20 ต.ค. เปิด
NOW = datetime(2026, 10, 20, 3, 0, tzinfo=UTC)
SESSION_START = 1792503000  # 2026-10-20 09:30 EDT
SESSION_END = 1792526400  # 2026-10-20 16:00 EDT


def _fixture():
    return json.loads(FIXTURE.read_text())


def _parse(data, now=NOW):
    return parse_chart(
        json.dumps(data).encode(), ticker="RKLB", now=now, ingested_at=now
    )


def test_parse_chart_returns_rounded_closes_by_trade_date():
    rows = _parse(_fixture())

    assert [(r.trade_date, r.close) for r in rows] == [
        ("2026-10-13", 64.22),
        ("2026-10-14", 59.18),
        ("2026-10-15", 55.25),
        ("2026-10-16", 50.84),
        ("2026-10-19", 51.36),
    ]
    assert rows[0].ticker == "RKLB"
    assert rows[0].source == "yahoo_finance"
    assert rows[0].ingested_at == "2026-10-20T03:00:00Z"


def test_daily_close_json_matches_docs_05_schema():
    row = _parse(_fixture())[-1]

    assert json.loads(row.to_json()) == {
        "ticker": "RKLB",
        "trade_date": "2026-10-19",
        "close": 51.36,
        "source": "yahoo_finance",
        "ingested_at": "2026-10-20T03:00:00Z",
    }


def test_skips_bar_of_session_that_is_still_open():
    data = _fixture()
    result = data["chart"]["result"][0]
    result["timestamp"].append(SESSION_START + 3600)
    result["indicators"]["quote"][0]["close"].append(52.0)

    during = datetime.fromtimestamp(SESSION_START + 7200, UTC)
    after_close = datetime.fromtimestamp(SESSION_END + 60, UTC)

    assert _parse(data, now=during)[-1].trade_date == "2026-10-19"
    assert _parse(data, now=after_close)[-1].trade_date == "2026-10-20"


def test_trade_date_uses_exchange_time_not_utc():
    data = _fixture()
    result = data["chart"]["result"][0]
    # 2026-10-17 02:00 UTC ยังเป็นวันที่ 16 ที่นิวยอร์ก
    result["timestamp"] = [int(datetime(2026, 10, 17, 2, 0, tzinfo=UTC).timestamp())]
    result["indicators"]["quote"][0]["close"] = [50.0]

    assert _parse(data)[0].trade_date == "2026-10-16"


def test_skips_days_without_close():
    data = _fixture()
    data["chart"]["result"][0]["indicators"]["quote"][0]["close"][1] = None

    dates = [r.trade_date for r in _parse(data)]

    assert "2026-10-14" not in dates
    assert len(dates) == 4


def test_chart_error_and_wrong_symbol_raise():
    error = {"chart": {"result": None, "error": {"code": "Not Found"}}}
    with pytest.raises(ValueError, match="chart error"):
        _parse(error)

    data = _fixture()
    data["chart"]["result"][0]["meta"]["symbol"] = "TSLA"
    with pytest.raises(ValueError, match="got TSLA"):
        _parse(data)


def _http_error(code):
    return urllib.error.HTTPError(
        "https://x", code, "err", email.message.Message(), None
    )


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


def _source(opener, sleeps=None):
    return YahooChart(
        opener=opener,
        sleep=(sleeps.append if sleeps is not None else lambda _: None),
        clock=lambda: NOW,
    )


def test_fetch_builds_url_with_period_and_parses():
    opener = FakeOpener([FIXTURE.read_bytes()])

    rows = _source(opener).fetch("RKLB", days=7)

    assert len(rows) == 5
    url = opener.urls[0]
    assert "/chart/RKLB?" in url
    assert "interval=1d" in url
    assert f"period2={int(NOW.timestamp())}" in url
    assert f"period1={int(NOW.timestamp()) - 7 * 86400}" in url


def test_fetch_retries_retryable_status_then_succeeds():
    sleeps = []
    opener = FakeOpener([_http_error(429), _http_error(503), FIXTURE.read_bytes()])
    source = _source(opener, sleeps)

    rows = source.fetch("RKLB", days=7)

    assert len(rows) == 5
    assert sleeps == [5.0, 10.0]
    assert source.stats.retries == 2
    assert source.stats.status_counts == {429: 1, 503: 1, 200: 1}


def test_fetch_fails_fast_on_404_and_on_bad_payload():
    with pytest.raises(FetchError, match="HTTP 404"):
        _source(FakeOpener([_http_error(404)])).fetch("XXXX", days=7)

    bad = json.dumps({"chart": {"result": None, "error": {"code": "Not Found"}}})
    with pytest.raises(FetchError, match="chart error"):
        _source(FakeOpener([bad.encode()])).fetch("XXXX", days=7)
