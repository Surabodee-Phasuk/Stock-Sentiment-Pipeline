from streaming.news_sentiment_job import (
    DEFAULT_CHECKPOINT,
    DEFAULT_SOURCE,
    DEFAULT_TARGET,
    build_parser,
)


def test_defaults_read_raw_and_write_news_sentiment():
    args = build_parser().parse_args([])

    assert args.source == DEFAULT_SOURCE == "glue.stock_sentiment.raw_news"
    assert args.target == DEFAULT_TARGET == "glue.stock_sentiment.news_sentiment"
    assert args.checkpoint == DEFAULT_CHECKPOINT
    assert args.checkpoint.endswith("/checkpoints/news_sentiment")
    assert args.model_name == "ProsusAI/finbert"
    assert args.once is False


def test_model_version_can_be_overridden():
    args = build_parser().parse_args(["--model-version", "finbert-v2", "--once"])

    assert args.model_version == "finbert-v2"
    assert args.once is True
