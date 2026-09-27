# Data Contracts (Draft Before Coding)

> These are planning contracts. Exact source fields may change after the chosen APIs/connectors are tested.

## 1. Stock Price Event
```json
{
  "event_id": "price_RKLB_20260922_100500",
  "ticker": "RKLB",
  "price": 28.50,
  "change_percent": 1.20,
  "timestamp": "2026-09-22T10:05:00Z",
  "source": "stock_api",
  "ingested_at": "2026-09-22T10:05:02Z"
}
```

## 2. News Event
```json
{
  "news_id": "news_001234",
  "ticker": "RKLB",
  "headline": "Rocket Lab secures new launch contract",
  "source": "RSS",
  "url": "https://example.com/news/1234",
  "published_at": "2026-09-22T10:05:00Z",
  "ingested_at": "2026-09-22T10:05:03Z"
}
```

## 3. Sentiment Event
```json
{
  "news_id": "news_001234",
  "ticker": "RKLB",
  "sentiment": "positive",
  "sentiment_score": 0.82,
  "model_name": "finbert",
  "processed_at": "2026-09-22T10:05:05Z"
}
```

## 4. Aggregated Sentiment
```json
{
  "ticker": "RKLB",
  "window_start": "2026-09-22T09:00:00Z",
  "window_end": "2026-09-22T10:00:00Z",
  "total_news": 20,
  "positive_count": 13,
  "neutral_count": 4,
  "negative_count": 3,
  "positive_percent": 65.0,
  "neutral_percent": 20.0,
  "negative_percent": 15.0,
  "average_sentiment_score": 0.42
}
```

## Conventions to lock before implementation
- Ticker field name: `ticker`
- Timestamp format: ISO 8601 / UTC for internal events
- Sentiment labels: `positive`, `neutral`, `negative`
- Preserve original source URL where available
- Keep `ingested_at` separate from source/event time
