import hashlib
import json
from datetime import UTC, datetime, timedelta, timezone

import pytest

from ingestion.news.event import NewsEvent, make_news_id, normalize_url, to_utc_iso


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (
            "https://finance.yahoo.com/news/x.html?.tsrc=rss",
            "https://finance.yahoo.com/news/x.html",
        ),
        ("http://www.Fool.com/a/b/", "https://fool.com/a/b"),
        ("https://example.com:443/a#section", "https://example.com/a"),
        ("https://example.com/a?b=2&a=1&utm_source=x", "https://example.com/a?a=1&b=2"),
        ("  https://example.com/a?fbclid=1  ", "https://example.com/a"),
    ],
)
def test_same_article_gets_same_news_id(a, b):
    assert normalize_url(a) == normalize_url(b)
    assert make_news_id(a) == make_news_id(b)


def test_different_articles_get_different_news_id():
    assert make_news_id("https://example.com/a?id=1") != make_news_id(
        "https://example.com/a?id=2"
    )
    assert make_news_id("https://example.com:8080/a") != make_news_id(
        "https://example.com/a"
    )


def test_news_id_is_sha256_of_normalized_url():
    expected = hashlib.sha256(b"https://example.com/a").hexdigest()
    assert make_news_id("https://www.example.com/a/") == expected


def test_normalize_rejects_relative_url():
    with pytest.raises(ValueError):
        normalize_url("/news/1234")


def test_to_utc_iso_converts_timezone():
    dt = datetime(2026, 10, 5, 9, 40, 2, 123456, tzinfo=timezone(timedelta(hours=-4)))
    assert to_utc_iso(dt) == "2026-10-05T13:40:02Z"


def test_to_utc_iso_rejects_naive_datetime():
    with pytest.raises(ValueError):
        to_utc_iso(datetime(2026, 10, 5, tzinfo=UTC).replace(tzinfo=None))


def test_event_matches_data_design_schema():
    event = NewsEvent.create(
        ticker="rklb",
        headline="  Rocket Lab   secures contract ",
        summary="",
        source="rss:yahoo",
        url="https://example.com/news/1234?.tsrc=rss",
        published_at=datetime(2026, 9, 22, 10, 5, tzinfo=UTC),
        ingested_at=datetime(2026, 9, 22, 10, 10, 3, tzinfo=UTC),
    )
    payload = json.loads(event.to_json())

    assert list(payload) == [
        "news_id",
        "ticker",
        "headline",
        "summary",
        "source",
        "url",
        "published_at",
        "ingested_at",
    ]
    assert payload["ticker"] == "RKLB"
    assert payload["headline"] == "Rocket Lab secures contract"
    assert payload["summary"] is None
    assert payload["url"] == "https://example.com/news/1234?.tsrc=rss"  # เก็บ URL ต้นทาง
    assert payload["news_id"] == make_news_id("https://example.com/news/1234")
    assert payload["published_at"] == "2026-09-22T10:05:00Z"
    assert payload["ingested_at"] == "2026-09-22T10:10:03Z"


def test_event_requires_headline():
    with pytest.raises(ValueError):
        NewsEvent.create(
            ticker="RKLB",
            headline="   ",
            summary=None,
            source="rss:yahoo",
            url="https://example.com/a",
            published_at=datetime(2026, 9, 22, tzinfo=UTC),
            ingested_at=datetime(2026, 9, 22, tzinfo=UTC),
        )
