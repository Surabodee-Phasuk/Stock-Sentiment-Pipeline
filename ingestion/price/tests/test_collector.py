import json

from ingestion.news.sources import FetchError
from ingestion.price.collector import collect, main, write_jsonl
from ingestion.price.sources import DailyClose


def _row(ticker, day, close=10.0):
    return DailyClose(
        ticker=ticker,
        trade_date=day,
        close=close,
        source="yahoo_finance",
        ingested_at="2026-10-20T03:00:00Z",
    )


class FakeSource:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def fetch(self, ticker, days):
        self.calls.append((ticker, days))
        result = self.results[ticker]
        if isinstance(result, Exception):
            raise result
        return result


def test_collect_gathers_rows_and_waits_between_tickers():
    source = FakeSource(
        {
            "AAPL": [_row("AAPL", "2026-10-16"), _row("AAPL", "2026-10-19")],
            "RKLB": [_row("RKLB", "2026-10-19")],
        }
    )
    sleeps = []

    stats = collect(
        source, ["AAPL", "RKLB"], days=7, delay_between_tickers=2.0, sleep=sleeps.append
    )

    assert source.calls == [("AAPL", 7), ("RKLB", 7)]
    assert sleeps == [2.0]
    assert len(stats.rows) == 3
    assert stats.per_ticker == {"AAPL": 2, "RKLB": 1}
    assert stats.latest_date == {"AAPL": "2026-10-19", "RKLB": "2026-10-19"}
    assert stats.failed_tickers == []


def test_collect_marks_failed_and_empty_tickers_but_keeps_going():
    source = FakeSource(
        {
            "AAPL": FetchError("HTTP 404"),
            "MSFT": [],
            "RKLB": [_row("RKLB", "2026-10-19")],
        }
    )

    stats = collect(source, ["AAPL", "MSFT", "RKLB"], days=7, sleep=lambda _: None)

    assert stats.failed_tickers == ["AAPL", "MSFT"]
    assert [r.ticker for r in stats.rows] == ["RKLB"]


def test_write_jsonl_overwrites_file_of_same_day(tmp_path):
    path = tmp_path / "price" / "daily_close_2026-10-20.jsonl"

    write_jsonl([_row("AAPL", "2026-10-16"), _row("AAPL", "2026-10-19")], path)
    write_jsonl([_row("RKLB", "2026-10-19", 51.36)], path)

    lines = path.read_text().splitlines()
    assert [json.loads(line) for line in lines] == [
        {
            "ticker": "RKLB",
            "trade_date": "2026-10-19",
            "close": 51.36,
            "source": "yahoo_finance",
            "ingested_at": "2026-10-20T03:00:00Z",
        }
    ]
    assert not list(path.parent.glob("*.tmp"))


def test_main_rejects_days_outside_range(capsys):
    for bad in ("0", "31"):
        try:
            main(["--days", bad])
        except SystemExit as exc:
            assert exc.code == 2
    assert "days must be 1-30" in capsys.readouterr().err
