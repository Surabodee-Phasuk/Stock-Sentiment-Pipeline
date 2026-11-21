from datetime import datetime, timezone
from pathlib import Path

from sentiment.finbert import FinBertClassifier
from sentiment.pipeline import (
    SENTIMENT_COLUMNS,
    SENTIMENT_SCHEMA,
    merge_sql,
    score_rows,
)
from sentiment.tests.test_finbert import fake_probs

ROOT = Path(__file__).resolve().parents[2]


def test_sentiment_columns_match_ddl_and_schema():
    ddl = (ROOT / "lakehouse" / "ddl" / "04_news_sentiment.sql").read_text("utf-8")
    start = ddl.index(".news_sentiment (") + len(".news_sentiment (")
    body = ddl[start : ddl.index("\n)")]
    ddl_cols = tuple(line.split()[0] for line in body.strip().splitlines())

    assert ddl_cols == SENTIMENT_COLUMNS
    schema_cols = tuple(part.split()[0] for part in SENTIMENT_SCHEMA.split(", "))
    assert schema_cols == SENTIMENT_COLUMNS


def test_merge_key_includes_model_version_and_only_inserts():
    sql = merge_sql("glue.stock_sentiment.news_sentiment", "u")

    assert (
        "ON t.news_id = s.news_id AND t.ticker = s.ticker "
        "AND t.model_version = s.model_version" in sql
    )
    assert sql.endswith("WHEN NOT MATCHED THEN INSERT *")
    assert "WHEN MATCHED" not in sql


def test_score_rows_builds_rows_in_ddl_order():
    clf = FinBertClassifier(model_version="test-v", prob_fn=fake_probs)
    published = datetime(2026, 11, 19, 14, 0, tzinfo=timezone.utc)
    when = datetime(2026, 11, 20, 0, 0, tzinfo=timezone.utc)
    rows = [
        {
            "news_id": "n1",
            "ticker": "NVDA",
            "published_at": published,
            "headline": "Nvidia beat estimates",
            "summary": None,
        },
        {
            "news_id": "n1",
            "ticker": "AMD",
            "published_at": published,
            "headline": "Rival",
            "summary": "AMD may miss",
        },
    ]

    out = score_rows(rows, clf, processed_at=when)

    assert out[0] == (
        "n1",
        "NVDA",
        published,
        "positive",
        0.88,
        "ProsusAI/finbert",
        "test-v",
        when,
    )
    assert out[1][1] == "AMD" and out[1][3] == "negative"
    assert len(out[0]) == len(SENTIMENT_COLUMNS)


def test_score_rows_empty():
    assert score_rows([], FinBertClassifier(prob_fn=fake_probs)) == []
