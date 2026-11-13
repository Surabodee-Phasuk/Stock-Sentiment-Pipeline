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
| Topic | Producer | Consumer | Key | Partitions |
|---|---|---|---|---|
| `stock-news` | news collector | Spark Structured Streaming | `ticker` | 3 (เก็บ 7 วัน) |

สร้าง topic ด้วย `kafka-init` ใน `infra/docker-compose.yml` เท่านั้น (ปิด auto-create topic ไว้)

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
Warehouse: `s3://stock-sentiment-lakehouse-surabodee/warehouse` ใน Spark อ้างถึงด้วย `glue.stock_sentiment.<table>`

DDL จริงอยู่ที่ `lakehouse/ddl/` สร้างด้วย `lakehouse/ddl/create_tables.py` (F2-01) ทุกตารางเป็น Iceberg format v2, Parquet + zstd, เวลาเป็น UTC

| ชั้น | Table | Partition (ร่าง) | เขียนโดย |
|---|---|---|---|
| Raw | `raw_news` | `days(published_at)` | Spark streaming (append) |
| Raw | `raw_daily_price` | `years(trade_date)` | Spark batch (append) |
| Cleaned | `clean_news` | `days(published_at)` | Spark streaming (MERGE on `news_id, ticker`, [ADR-0007](adr/0007-clean-news-key-news-id-ticker.md)) |
| Cleaned | `news_sentiment` | `days(published_at)` | Spark streaming / reprocess job |
| Cleaned | `daily_price` | `years(trade_date)` | Spark batch (MERGE on `ticker, trade_date`) |
| Aggregated | `sentiment_daily` | `years(trade_date)` | Spark batch |

Partition spec ล็อกหลัง benchmark (issue F2-07)

### `raw_news`
event ทุกตัวจาก Kafka ตามที่รับมา append อย่างเดียว ไม่ตัดซ้ำ (F2-02)

| column | type | หมายเหตุ |
|---|---|---|
| news_id, ticker, headline, summary, source, url | string | ตาม News event |
| published_at, ingested_at | timestamp | ตาม News event |
| kafka_partition | int | ตำแหน่งใน Kafka ใช้ตามรอยกลับ |
| kafka_offset | bigint | |
| kafka_timestamp | timestamp | |
| raw_value | string | JSON ต้นฉบับ reprocess ได้แม้ schema event เปลี่ยน |
| loaded_at | timestamp | เวลาที่ Spark เขียน ใช้วัด latency |

### `clean_news`
หนึ่งแถวต่อ **`(news_id, ticker)`** หลังตัดซ้ำและ validate (F2-03, ADR-0007)

| column | type | หมายเหตุ |
|---|---|---|
| news_id | string | key |
| ticker | string | key |
| headline, summary, source, url | string | `source` = แหล่งแรกที่เจอ |
| published_at, ingested_at | timestamp | `ingested_at` = ครั้งแรกที่เจอ |
| cleaned_at | timestamp | เวลาที่ MERGE |

### `raw_daily_price`
ทุกแถวจากไฟล์ของ F1-02 append อย่างเดียว (F2-04)

| column | type |
|---|---|
| ticker | string |
| trade_date | date |
| close | double |
| source | string |
| ingested_at | timestamp |
| loaded_at | timestamp |

### `daily_price`
หนึ่งแถวต่อ **`(ticker, trade_date)`** (F2-04)

| column | type |
|---|---|
| ticker | string |
| trade_date | date |
| close | double |
| source | string |
| ingested_at | timestamp |
| updated_at | timestamp |

### `news_sentiment`
หนึ่งแถวต่อ **`(news_id, ticker, model_version)`** (F3-01, F3-04)

| column | type |
|---|---|
| news_id | string |
| ticker | string |
| published_at | timestamp |
| sentiment | string |
| sentiment_score | double |
| model_name | string |
| model_version | string |
| processed_at | timestamp |

### `sentiment_daily`
หนึ่งแถวต่อ **`(ticker, trade_date, model_version)`** (F4-01)

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
| computed_at | timestamp |
