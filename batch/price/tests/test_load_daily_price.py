from pathlib import Path

import pytest

from batch.price.load_daily_price import (
    DEFAULT_INPUT,
    DEFAULT_RAW,
    DEFAULT_TARGET,
    PRICE_COLUMNS,
    RAW_COLUMNS,
    build_parser,
    load_tickers,
    merge_sql,
    reject_reason_sql,
)

ROOT = Path(__file__).resolve().parents[3]


def _ddl_columns(file, table):
    ddl = (ROOT / "lakehouse" / "ddl" / file).read_text(encoding="utf-8")
    start = ddl.index(f".{table} (") + len(f".{table} (")
    body = ddl[start : ddl.index("\n)")]
    return tuple(line.split()[0] for line in body.strip().splitlines())


def test_columns_match_ddl():
    assert _ddl_columns("02_raw_daily_price.sql", "raw_daily_price") == RAW_COLUMNS
    assert _ddl_columns("05_daily_price.sql", "daily_price") == PRICE_COLUMNS


def test_loads_the_ten_poc_tickers():
    tickers = load_tickers()

    assert len(tickers) == 10
    assert tickers[0] == "AAPL" and "RKLB" in tickers and "SPCX" in tickers


def test_load_tickers_rejects_empty_file(tmp_path):
    empty = tmp_path / "tickers.yaml"
    empty.write_text("tickers: []\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_tickers(empty)


def test_reject_reasons_in_order():
    sql = reject_reason_sql(["AAPL", "RKLB"])

    reasons = ["'missing_field'", "'bad_close'", "'bad_trade_date'", "'unknown_ticker'"]
    positions = [sql.index(r) for r in reasons]
    assert positions == sorted(positions)
    assert "close <= 0" in sql
    assert "ticker NOT IN ('AAPL', 'RKLB')" in sql
    assert sql.startswith("CASE ") and sql.endswith(" END")


def test_merge_keys_on_ticker_and_trade_date_and_keeps_newest():
    sql = merge_sql("glue.stock_sentiment.daily_price", "updates")

    assert "ON t.ticker = s.ticker AND t.trade_date = s.trade_date" in sql
    assert "WHEN MATCHED AND s.ingested_at > t.ingested_at THEN UPDATE" in sql
    assert "WHEN NOT MATCHED THEN INSERT *" in sql


def test_defaults_read_collector_output_and_project_tables():
    args = build_parser().parse_args([])

    assert args.input == DEFAULT_INPUT
    assert DEFAULT_INPUT.endswith("data/price/daily_close_*.jsonl")
    assert args.raw_table == DEFAULT_RAW == "glue.stock_sentiment.raw_daily_price"
    assert args.target == DEFAULT_TARGET == "glue.stock_sentiment.daily_price"
