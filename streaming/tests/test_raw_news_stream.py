import re
from pathlib import Path

from streaming.raw_news_stream import (
    DEFAULT_CHECKPOINT,
    DEFAULT_TABLE,
    build_parser,
)

ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / "streaming" / "raw_news_stream.py"


def test_defaults_point_to_project_table_and_s3_checkpoint(monkeypatch):
    monkeypatch.delenv("KAFKA_BOOTSTRAP_SERVERS", raising=False)
    monkeypatch.delenv("KAFKA_TOPIC", raising=False)

    args = build_parser().parse_args([])

    assert args.bootstrap_servers == "kafka:19092"
    assert args.topic == "stock-news"
    assert args.table == DEFAULT_TABLE == "glue.stock_sentiment.raw_news"
    assert args.checkpoint == DEFAULT_CHECKPOINT
    assert args.checkpoint.startswith("s3a://stock-sentiment-lakehouse-surabodee/")
    assert args.trigger_seconds == 60
    assert args.once is False


def test_selected_columns_match_raw_news_table_order():
    # ลำดับคอลัมน์ต้องตรงกับ lakehouse/ddl/01_raw_news.sql (F2-01)
    expected = [
        "news_id",
        "ticker",
        "headline",
        "summary",
        "source",
        "url",
        "published_at",
        "ingested_at",
        "kafka_partition",
        "kafka_offset",
        "kafka_timestamp",
        "raw_value",
        "loaded_at",
    ]

    source = STREAM.read_text(encoding="utf-8")
    select = source[source.index("kafka_df.select(") : source.index("def main")]

    assert re.findall(r'\.alias\(\s*"(\w+)"', select) == expected
