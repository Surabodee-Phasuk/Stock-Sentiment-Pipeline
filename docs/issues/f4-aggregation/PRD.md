# PRD: F4 — Aggregation & Serving API

สรุป sentiment รายหุ้นรายวันเทียบราคาปิด และ API ที่เว็บแอปเรียกผ่าน Athena

**อ้างอิง:** FR-3.3 ใน [docs/04-requirements.md](../../04-requirements.md)  
**Milestones:** M6

## Issues

| # | งาน | Owner | Phase | Branch |
|---|---|---|---|---|
| [01](issues/01-sentiment-daily.md) | Spark batch: `sentiment_daily` (sentiment รายวัน + ราคาปิด) | M2 | Full (T2/2570) | `feat/f4-01-sentiment-daily` |
| [02](issues/02-query-api.md) | API layer: endpoint สำหรับ Search / Home / Stock Detail ผ่าน Athena | M2 | Full (T2/2570) | `feat/f4-02-query-api` |
