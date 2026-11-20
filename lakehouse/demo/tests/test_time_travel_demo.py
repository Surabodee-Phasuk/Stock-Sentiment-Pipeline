from lakehouse.demo.time_travel_schema_evolution import (
    DEMO_TABLE,
    build_parser,
    demo_create_sql,
    sample_sql,
)

PRODUCTION_TABLES = {
    "raw_news",
    "raw_daily_price",
    "clean_news",
    "news_sentiment",
    "daily_price",
    "sentiment_daily",
}


def test_demo_never_writes_to_production_tables():
    assert DEMO_TABLE.startswith("zz_")
    assert DEMO_TABLE not in PRODUCTION_TABLES


def test_defaults_read_raw_news_in_glue():
    args = build_parser().parse_args([])

    assert (args.catalog, args.database, args.source) == (
        "glue",
        "stock_sentiment",
        "raw_news",
    )
    assert args.keep is False


def test_demo_table_is_iceberg_v2_partitioned_by_day():
    sql = demo_create_sql("glue.stock_sentiment.zz_f205_demo")

    assert "USING iceberg" in sql
    assert "PARTITIONED BY (days(published_at))" in sql
    assert "'format-version' = '2'" in sql


def test_sample_takes_unique_news_in_non_overlapping_batches():
    first = sample_sql("glue.stock_sentiment.raw_news", 30, 0)
    second = sample_sql("glue.stock_sentiment.raw_news", 10, 30)

    assert "PARTITION BY news_id, ticker" in first
    assert "rn = 1" in first
    assert first.endswith("LIMIT 30 OFFSET 0")
    assert second.endswith("LIMIT 10 OFFSET 30")
