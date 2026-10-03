# Data Contracts (Draft)

> สัญญาข้อมูลฉบับร่าง ฟิลด์จริงอาจเปลี่ยนหลังทดสอบ API ที่เลือก ราคามีเฉพาะ **ราคาปิดรายวัน** (ไม่มีราคาระหว่างวัน)

## 1. Daily Close Price (batch, Yahoo Finance)
```json
{
  "ticker": "RKLB",
  "trade_date": "2026-09-22",
  "close": 28.50,
  "source": "yahoo_finance",
  "ingested_at": "2026-09-23T01:00:02Z"
}
```

## 2. News Event (streaming, RSS / News API)
```json
{
  "news_id": "news_001234",
  "ticker": "RKLB",
  "headline": "Rocket Lab secures new launch contract",
  "source": "RSS",
  "url": "https://example.com/news/1234",
  "published_at": "2026-09-22T10:05:00Z",
  "ingested_at": "2026-09-22T10:10:03Z"
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
  "model_version": "v1",
  "processed_at": "2026-09-22T10:10:05Z"
}
```
`model_version` ช่วยให้ประมวลผล sentiment ใหม่จากชั้น Raw เมื่อเปลี่ยนโมเดลได้ และเทียบผลระหว่างเวอร์ชัน

## 4. Daily Aggregated Sentiment
```json
{
  "ticker": "RKLB",
  "date": "2026-09-22",
  "total_news": 20,
  "positive_count": 13,
  "neutral_count": 4,
  "negative_count": 3,
  "positive_percent": 65.0,
  "neutral_percent": 20.0,
  "negative_percent": 15.0,
  "average_sentiment_score": 0.42,
  "close": 28.50
}
```

## Conventions
- Ticker field: `ticker`
- Timestamp: ISO 8601 / UTC; วันซื้อขายใช้ `trade_date` / `date`
- Sentiment labels: `positive`, `neutral`, `negative`
- เก็บ URL ต้นทางของข่าวไว้เสมอ (ใช้เป็นแหล่งอ้างอิงของ RAG)
- `ingested_at` แยกจากเวลาเผยแพร่ข่าว (ใช้วัด latency ≤ 15 นาที)
- ไม่มีข้อมูลโซเชียลหรือราคาระหว่างวัน
