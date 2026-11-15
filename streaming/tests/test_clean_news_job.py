from pathlib import Path

import pytest

from streaming.clean_news_job import (
    CLEAN_COLUMNS,
    DEFAULT_CHECKPOINT,
    DEFAULT_SOURCE,
    DEFAULT_TARGET,
    build_parser,
    load_tickers,
    merge_sql,
    reject_reason_sql,
)

ROOT = Path(__file__).resolve().parents[2]


def test_loads_the_ten_poc_tickers_from_config():
    assert load_tickers() == [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "META",
        "TSLA",
        "AVGO",
        "RKLB",
        "SPCX",
    ]


def test_load_tickers_rejects_empty_file(tmp_path):
    empty = tmp_path / "tickers.yaml"
    empty.write_text("tickers: []\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_tickers(empty)


def test_clean_columns_match_clean_news_ddl():
    ddl = (ROOT / "lakehouse" / "ddl" / "03_clean_news.sql").read_text("utf-8")
    # ข้ามบรรทัด comment ด้านบนที่มีวงเล็บ เริ่มอ่านหลังชื่อตาราง
    start = ddl.index(".clean_news (") + len(".clean_news (")
    body = ddl[start : ddl.index("\n)")]

    assert tuple(line.split()[0] for line in body.strip().splitlines()) == CLEAN_COLUMNS


def test_reject_reasons_cover_issue_rules_in_order():
    sql = reject_reason_sql(["AAPL", "RKLB"])

    missing = sql.index("'missing_field'")
    bad_time = sql.index("'bad_timestamp'")
    unknown = sql.index("'unknown_ticker'")
    assert missing < bad_time < unknown
    assert "ticker NOT IN ('AAPL', 'RKLB')" in sql
    assert "published_at > loaded_at + INTERVAL 1 HOURS" in sql
    assert sql.startswith("CASE ") and sql.endswith(" END")


def test_merge_uses_adr_0007_key_and_only_inserts():
    sql = merge_sql("glue.stock_sentiment.clean_news", "updates")

    assert "ON t.news_id = s.news_id AND t.ticker = s.ticker" in sql
    assert "WHEN NOT MATCHED THEN INSERT *" in sql
    assert "WHEN MATCHED" not in sql


def test_defaults_point_to_project_tables_and_s3_checkpoint():
    args = build_parser().parse_args([])

    assert args.source == DEFAULT_SOURCE == "glue.stock_sentiment.raw_news"
    assert args.target == DEFAULT_TARGET == "glue.stock_sentiment.clean_news"
    assert args.checkpoint == DEFAULT_CHECKPOINT
    assert args.checkpoint.endswith("/checkpoints/clean_news")
    assert args.once is False
