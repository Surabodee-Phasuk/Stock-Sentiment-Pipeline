# PRD: F1 — Ingestion — ข่าวและราคาปิด

ดึงข่าวภาษาอังกฤษจาก RSS / News API ทุก 5–15 นาทีเข้า Kafka และดึงราคาปิดรายวันจาก Yahoo Finance

**อ้างอิง:** FR-1.1–FR-1.5 ใน [docs/04-requirements.md](../../04-requirements.md)  
**Milestones:** M2, M6

## Issues

| # | งาน | Owner | Phase | Branch |
|---|---|---|---|---|
| [01](issues/01-news-collector.md) | News collector RSS / News API → Kafka (10 หุ้น) | M1 | PoC (T1/2569) | `feat/f1-01-news-collector` |
| [02](issues/02-yahoo-daily-close.md) | Yahoo Finance daily close collector (10 หุ้น) | M1 | PoC (T1/2569) | `feat/f1-02-yahoo-daily-close` |
| [03](issues/03-multi-source-news.md) | รวมหลายแหล่งข่าวและตัดซ้ำเบื้องต้นที่ collector | M1 | PoC (T1/2569) | `feat/f1-03-multi-source-news` |
| [04](issues/04-backfill-2020.md) | Backfill ข่าวและราคาปิดย้อนหลังตั้งแต่ปี 2020 สำหรับ ~50 หุ้น | M1 | Full (T2/2570) | `feat/f1-04-backfill-2020` |
