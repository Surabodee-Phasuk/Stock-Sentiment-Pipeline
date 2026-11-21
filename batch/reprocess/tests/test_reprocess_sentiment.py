import ast
from datetime import date
from pathlib import Path

import pytest

from batch.reprocess.reprocess_sentiment import (
    DEFAULT_SOURCE,
    DEFAULT_TARGET,
    build_parser,
    date_filter,
)


def test_requires_new_model_version():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_defaults_read_raw_layer_only():
    args = build_parser().parse_args(["--model-version", "finbert-v2"])

    assert args.source == DEFAULT_SOURCE == "glue.stock_sentiment.raw_news"
    assert args.target == DEFAULT_TARGET == "glue.stock_sentiment.news_sentiment"
    assert args.model_version == "finbert-v2"
    assert args.since is None and args.until is None


def test_date_filter():
    assert date_filter(None, None) is None
    assert date_filter(date(2026, 11, 1), None) == (
        "published_at >= TIMESTAMP '2026-11-01'"
    )
    assert date_filter(date(2026, 11, 1), date(2026, 11, 20)) == (
        "published_at >= TIMESTAMP '2026-11-01' "
        "AND published_at < TIMESTAMP '2026-11-20'"
    )


def test_does_not_fetch_news_from_sources():
    """FR-2.6: reprocess อ่านจาก Raw เท่านั้น ห้าม import collector หรือ Kafka."""
    src = Path(__file__).resolve().parents[1] / "reprocess_sentiment.py"
    imported = {
        (n.module or "") if isinstance(n, ast.ImportFrom) else a.name
        for n in ast.walk(ast.parse(src.read_text("utf-8")))
        if isinstance(n, ast.Import | ast.ImportFrom)
        for a in n.names
    }

    assert not any(m.startswith(("ingestion", "confluent_kafka")) for m in imported)
