import re

import pytest

from lakehouse.ddl.create_tables import load_statements, main

# ชั้นและ partition ตามตาราง "Iceberg tables" ใน docs/05
EXPECTED = {
    "raw_news": "days(published_at)",
    "raw_daily_price": "years(trade_date)",
    "clean_news": "days(published_at)",
    "news_sentiment": "days(published_at)",
    "daily_price": "years(trade_date)",
    "sentiment_daily": "years(trade_date)",
}


def _columns(sql):
    body = sql[sql.index("(") + 1 : sql.index("\n)")]
    return [line.split()[0] for line in body.strip().splitlines()]


def test_loads_all_six_tables_in_layer_order():
    tables = [s.table for s in load_statements()]

    assert tables == [
        "raw_news",
        "raw_daily_price",
        "clean_news",
        "news_sentiment",
        "daily_price",
        "sentiment_daily",
    ]


def test_every_table_is_idempotent_iceberg_with_expected_partition():
    for stmt in load_statements():
        assert stmt.sql.startswith(
            f"CREATE TABLE IF NOT EXISTS glue.stock_sentiment.{stmt.table} ("
        )
        assert "USING iceberg" in stmt.sql
        assert f"PARTITIONED BY ({EXPECTED[stmt.table]})" in stmt.sql
        assert "'format-version' = '2'" in stmt.sql
        assert "${" not in stmt.sql
        assert "--" not in stmt.sql


def test_partition_column_exists_in_each_table():
    for stmt in load_statements():
        column = re.search(r"\((\w+)\)", EXPECTED[stmt.table]).group(1)
        assert column in _columns(stmt.sql), stmt.table


@pytest.mark.parametrize(
    ("table", "keys"),
    [
        ("clean_news", ["news_id", "ticker"]),  # ADR-0007
        ("news_sentiment", ["news_id", "ticker", "model_version"]),
        ("daily_price", ["ticker", "trade_date"]),
        ("sentiment_daily", ["ticker", "trade_date", "model_version"]),
    ],
)
def test_merge_key_columns_exist(table, keys):
    stmt = next(s for s in load_statements() if s.table == table)

    assert set(keys) <= set(_columns(stmt.sql))
    assert f"key ({', '.join(keys)})" in stmt.sql


def test_raw_news_keeps_event_fields_and_kafka_position():
    stmt = next(s for s in load_statements() if s.table == "raw_news")
    news_event_fields = [
        "news_id",
        "ticker",
        "headline",
        "summary",
        "source",
        "url",
        "published_at",
        "ingested_at",
    ]

    columns = _columns(stmt.sql)
    assert columns[: len(news_event_fields)] == news_event_fields
    assert {"kafka_partition", "kafka_offset", "raw_value", "loaded_at"} <= set(columns)


def test_catalog_and_database_can_be_overridden():
    stmt = load_statements(catalog="local", database="scratch")[0]

    assert stmt.sql.startswith("CREATE TABLE IF NOT EXISTS local.scratch.raw_news (")


def test_dry_run_prints_sql_without_spark(capsys):
    assert main(["--dry-run"]) == 0

    out = capsys.readouterr().out
    assert out.count("CREATE TABLE IF NOT EXISTS") == 6
    assert "-- 03_clean_news.sql" in out
