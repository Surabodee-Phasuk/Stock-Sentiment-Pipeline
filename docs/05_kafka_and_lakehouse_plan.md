# Kafka and Lakehouse Plan

## Kafka Topics
| Topic | Producer | Consumer | Purpose |
|---|---|---|---|
| `stock-news` | News collector (RSS / News API, ทุก 5–15 นาที) | Spark Structured Streaming | ข่าวใหม่ |

ราคาปิดรายวันไม่ผ่าน Kafka: ดึงวันละครั้งด้วย Spark batch แล้วเขียนลง Iceberg ตรง

## Lakehouse: Amazon S3 + Apache Iceberg (Glue catalog, Athena query)
ข่าวที่เข้าแบบ streaming กับราคาปิดที่เข้าแบบ batch อยู่ในตารางชุดเดียวกัน และ query รวมกันผ่าน Athena ได้

### Raw
ข่าวดิบ เก็บไว้ประมวลผล sentiment ใหม่ได้เมื่อเปลี่ยนโมเดล (reprocess)

### Cleaned
ตัดข่าวซ้ำ (duplicate rate = 0%) + sentiment จาก FinBERT; เป็นแหล่งข้อมูลของ LLM และ RAG

### Aggregated
สรุปรายหุ้นรายวัน (sentiment distribution, จำนวนข่าว, ราคาปิด) ที่เว็บแอปอ่านผ่าน Athena

## Suggested tables
- `raw_news`
- `raw_daily_price`
- `clean_news`
- `sentiment_events`
- `sentiment_daily`
- `price_sentiment_daily`

## Capabilities to demonstrate
- time travel: ย้อนดูตาราง ณ เวลาก่อนหน้า
- schema evolution
- reprocess sentiment ใหม่จากชั้น Raw โดยไม่ต้องดึงข่าวจากแหล่งใหม่
- ทำงานต่อเนื่อง ≥ 7 วัน กู้คืนจาก checkpoint ได้ ไม่สูญหายข่าว

## Partitioning
ทดสอบเทียบมีและไม่มี partition (ticker / date) ด้วย query เวลาและข้อมูลที่ Athena สแกน ก่อนล็อก partition spec; เป้าหมาย query ≤ 5 วินาที
