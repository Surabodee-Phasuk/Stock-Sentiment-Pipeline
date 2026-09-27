# Kafka and Lakehouse Plan

## Kafka Topics
| Topic | Producer | Main Consumer | Purpose |
|---|---|---|---|
| `stock-price` | Stock API collector | Spark | Streaming price events |
| `stock-news` | News/RSS/X collector | Spark | Raw news events |
| `sentiment-result` | Spark + sentiment stage | Downstream/storage stage | Sentiment output events |

## Lakehouse Layers
### Raw
Original/sourced events retained for traceability and debugging.

### Cleaned
Validated and normalized records. Expected checks include schema, nulls, duplicates, timestamps, and abnormal values where applicable.

### Aggregated
Dashboard-ready summaries such as sentiment distribution by ticker/time window, news counts, and relevant price-window outputs.

## Suggested logical data sets
- `raw_stock_price`
- `raw_news`
- `clean_stock_price`
- `clean_news`
- `sentiment_events`
- `sentiment_hourly`
- `price_sentiment_hourly`

## Initial partitioning idea
Prefer partitioning strategies that support common dashboard filters such as ticker and date/time. Do not lock the physical partition spec until sample data volume and query patterns are measured.
