import pytest

from webapp.api.athena import (
    AthenaClient,
    AthenaConfig,
    AthenaError,
    daily_sql,
    news_sql,
    parse_rows,
    stock_detail,
    today_sql,
)

CFG = AthenaConfig(
    workgroup="wg", database="stock_sentiment", model_version="finbert-v1"
)


def page(columns, rows, header=True):
    meta = [{"Name": n, "Type": t} for n, t in columns]
    data = [{"Data": [{"VarCharValue": n} for n, _ in columns]}] if header else []
    for r in rows:
        data.append({"Data": [{} if v is None else {"VarCharValue": v} for v in r]})
    return {"ResultSet": {"ResultSetMetadata": {"ColumnInfo": meta}, "Rows": data}}


def test_parse_rows_converts_types_and_skips_header_once():
    cols = [
        ("date", "date"),
        ("close", "double"),
        ("news", "bigint"),
        ("at", "timestamp"),
    ]
    p1 = page(cols, [("2026-11-18", "140.5", "3", "2026-11-18 14:00:00.000000")])
    p2 = page(cols, [("2026-11-19", "141", "0", None)], header=False)

    assert parse_rows([p1, p2]) == [
        {"date": "2026-11-18", "close": 140.5, "news": 3, "at": "2026-11-18T14:00:00Z"},
        {"date": "2026-11-19", "close": 141.0, "news": 0, "at": None},
    ]


def test_sql_filters_ticker_version_and_uses_new_york_date():
    sql = daily_sql("stock_sentiment", "NVDA", "finbert-v1", 30)

    assert "ticker = 'NVDA' AND model_version = 'finbert-v1'" in sql
    assert "AT TIME ZONE 'America/New_York' AS date" in sql
    assert "LEFT JOIN agg a ON a.d = p.trade_date" in sql
    assert "LIMIT 30" in sql
    assert "JOIN stock_sentiment.clean_news c" in news_sql(
        "stock_sentiment", "NVDA", "v", 5
    )
    assert "INTERVAL '24' HOUR" in today_sql("stock_sentiment", "NVDA", "v")


@pytest.mark.parametrize("bad", ["NVDA'; DROP TABLE x --", "a b", ""])
def test_sql_rejects_unsafe_values(bad):
    with pytest.raises(ValueError):
        daily_sql("db", bad, "v1", 30)


def fake_run(sql):
    if "FROM stock_sentiment.daily_price p" in sql:  # ล่าสุดก่อน (ORDER BY DESC)
        return [
            {"date": "2026-11-19", "close": 145.0, "news": 2, "positive": 1,
             "neutral": 0, "negative": 1, "avg_score": 0.123456},
            {"date": "2026-11-18", "close": 140.0, "news": 0, "positive": 0,
             "neutral": 0, "negative": 0, "avg_score": None},
        ]  # fmt: skip
    if "JOIN stock_sentiment.clean_news" in sql:
        return [
            {"headline": "Nvidia beats", "source": "rss:yahoo", "url": "u",
             "published_at": "2026-11-19T15:00:00Z", "sentiment": "positive",
             "score": 0.8261},
        ]  # fmt: skip
    return [
        {"news": 2, "positive": 1, "neutral": 0, "negative": 1,
         "updated_at": "2026-11-19T15:05:00Z"},
    ]  # fmt: skip


def test_stock_detail_has_same_shape_as_mock_data():
    s = stock_detail("NVDA", fake_run, CFG)

    assert s["close"] == 145.0 and s["prev_close"] == 140.0
    assert s["trade_date"] == "2026-11-19"
    assert [d["date"] for d in s["daily"]] == ["2026-11-18", "2026-11-19"]  # เก่า → ใหม่
    assert s["daily"][1]["avg_score"] == 0.123
    assert s["news"][0]["source"] == "Yahoo" and s["news"][0]["score"] == 0.826
    assert s["today"] == {"news": 2, "positive": 1, "neutral": 0, "negative": 1}
    assert s["updated_at"] == "2026-11-19T15:05:00Z"


class FakeBoto:
    def __init__(self, states):
        self.states = list(states)
        self.stopped = False

    def start_query_execution(self, **kw):
        assert kw["WorkGroup"] == "wg"
        assert kw["QueryExecutionContext"] == {"Database": "stock_sentiment"}
        return {"QueryExecutionId": "q1"}

    def get_query_execution(self, QueryExecutionId):
        state = self.states.pop(0) if len(self.states) > 1 else self.states[0]
        return {
            "QueryExecution": {"Status": {"State": state, "StateChangeReason": "boom"}}
        }

    def stop_query_execution(self, QueryExecutionId):
        self.stopped = True

    def get_paginator(self, name):
        class P:
            def paginate(self, QueryExecutionId):
                return [page([("n", "integer")], [("7",)])]

        return P()


def test_client_polls_until_succeeded():
    client = AthenaClient(CFG, FakeBoto(["RUNNING", "SUCCEEDED"]))

    assert client.query("SELECT 7") == [{"n": 7}]


def test_client_raises_on_failed_query():
    with pytest.raises(AthenaError, match="boom"):
        AthenaClient(CFG, FakeBoto(["FAILED"])).query("SELECT x")


def test_client_stops_query_after_timeout():
    cfg = AthenaConfig(workgroup="wg", timeout_seconds=0.0)
    boto = FakeBoto(["RUNNING"])

    with pytest.raises(AthenaError, match="timed out"):
        AthenaClient(cfg, boto).query("SELECT 1")
    assert boto.stopped


def test_client_turns_boto_errors_into_athena_error():
    class NoCredentialsError(Exception):
        pass

    NoCredentialsError.__module__ = "botocore.exceptions"

    class Broken(FakeBoto):
        def start_query_execution(self, **kw):
            raise NoCredentialsError("secret detail")

    with pytest.raises(AthenaError, match="^NoCredentialsError$"):
        AthenaClient(CFG, Broken(["SUCCEEDED"])).query("SELECT 1")


def test_client_does_not_hide_programming_errors():
    class Broken(FakeBoto):
        def start_query_execution(self, **kw):
            raise KeyError("bug")

    with pytest.raises(KeyError):
        AthenaClient(CFG, Broken(["SUCCEEDED"])).query("SELECT 1")
