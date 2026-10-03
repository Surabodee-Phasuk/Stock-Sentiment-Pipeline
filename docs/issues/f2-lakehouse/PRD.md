# PRD: F2 — Lakehouse — S3 + Iceberg

ตาราง Iceberg ชั้น Raw / Cleaned / Aggregated บน S3 ที่รับทั้งข่าว streaming และราคาปิด batch และพิสูจน์ความสามารถของ Lakehouse

**อ้างอิง:** FR-2.1–FR-2.6, NFR-2–NFR-4 ใน [docs/04-requirements.md](../../04-requirements.md)  
**Milestones:** M3, M6

## Issues

| # | งาน | Owner | Phase | Branch |
|---|---|---|---|---|
| [01](issues/01-iceberg-tables.md) | DDL ตาราง Iceberg ทั้งสามชั้นใน Glue | M1 | PoC (T1/2569) | `feat/f2-01-iceberg-tables` |
| [02](issues/02-kafka-to-raw-streaming.md) | Spark Structured Streaming: Kafka → `raw_news` พร้อม checkpoint | M1 | PoC (T1/2569) | `feat/f2-02-kafka-to-raw-streaming` |
| [03](issues/03-dedup-to-cleaned.md) | ตัดข่าวซ้ำ: `raw_news` → `clean_news` ด้วย MERGE | M1 | PoC (T1/2569) | `feat/f2-03-dedup-to-cleaned` |
| [04](issues/04-price-batch-load.md) | Spark batch: ราคาปิด → `raw_daily_price` / `daily_price` | M2 | PoC (T1/2569) | `feat/f2-04-price-batch-load` |
| [05](issues/05-time-travel-schema-evolution.md) | สาธิต time travel และ schema evolution | M1 | PoC (T1/2569) | `exp/f2-05-time-travel-schema-evolution` |
| [06](issues/06-scale-50-tickers.md) | ขยาย pipeline เป็น ~50 หุ้นและข้อมูลตั้งแต่ 2020 | M1 | Full (T2/2570) | `feat/f2-06-scale-50-tickers` |
| [07](issues/07-partition-benchmark.md) | Benchmark partition และล็อก partition spec | M1 | Full (T2/2570) | `test/f2-07-partition-benchmark` |
