# 05 — Data Design

> สัญญาข้อมูลฉบับร่าง ฟิลด์จริงอาจเปลี่ยนหลังทดสอบ API (การเปลี่ยน schema ต้องแก้หน้านี้ใน PR เดียวกัน)

## Conventions
- Ticker: `ticker` (ตัวพิมพ์ใหญ่)
- เวลา: ISO 8601 / UTC; วันซื้อขาย: `trade_date` (DATE)
- Sentiment labels: `positive`, `neutral`, `negative`
- เก็บ `url` ต้นทางเสมอ (ใช้อ้างอิงใน RAG)
- `ingested_at` แยกจาก `published_at` (ใช้วัด latency)
- ไม่มีข้อมูลโซเชียลหรือราคาระหว่างวัน

## Kafka
| Topic | Producer | Consumer | Key |
|---|---|---|---|
| `stock-news` | news collector | Spark Structured Streaming | `ticker` |

ราคาปิดไม่ผ่าน Kafka: Spark batch เขียนลง Iceberg ตรง

## Events

### News event (`stock-news`)
```json
{
  "news_id": "sha256(url)",
  "ticker": "RKLB",
  "headline": "Rocket Lab secures new launch contract",
  "summary": "optional source summary",
  "source": "rss:yahoo",
  "url": "https://example.com/news/1234",
  "published_at": "2026-09-22T10:05:00Z",
  "ingested_at": "2026-09-22T10:10:03Z"
}
```
`news_id` = hash ของ URL ที่ normalize แล้ว → ใช้ตัดข่าวซ้ำ

### Daily close (batch)
```json
{ "ticker": "RKLB", "trade_date": "2026-09-22", "close": 28.50, "source": "yahoo_finance", "ingested_at": "2026-09-23T01:00:02Z" }
```

## Iceberg tables (Glue database `stock_sentiment`)
| ชั้น | Table | Partition (ร่าง) | เขียนโดย |
|---|---|---|---|
| Raw | `raw_news` | `days(published_at)` | Spark streaming (append) |
| Raw | `raw_daily_price` | `years(trade_date)` | Spark batch (append) |
| Cleaned | `clean_news` | `days(published_at)` | Spark streaming (MERGE on `news_id`) |
| Cleaned | `news_sentiment` | `days(published_at)` | Spark streaming / reprocess job |
| Cleaned | `daily_price` | `years(trade_date)` | Spark batch (MERGE on `ticker, trade_date`) |
| Aggregated | `sentiment_daily` | `years(trade_date)` | Spark batch |

Partition spec ล็อกหลัง benchmark (issue F2-07)

### `news_sentiment`
| column | type |
|---|---|
| news_id | string |
| ticker | string |
| sentiment | string |
| sentiment_score | double |
| model_name | string |
| model_version | string |
| processed_at | timestamp |

### `sentiment_daily`
| column | type |
|---|---|
| ticker | string |
| trade_date | date |
| total_news | int |
| positive_count / neutral_count / negative_count | int |
| positive_pct / neutral_pct / negative_pct | double |
| avg_sentiment_score | double |
| close | double |
| close_change_pct | double |
| model_version | string |
