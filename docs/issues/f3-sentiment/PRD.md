# PRD: F3 — Sentiment — FinBERT

จำแนก sentiment รายข่าวด้วย FinBERT ใน streaming, วัดคุณภาพกับ gold set และ reprocess จาก Raw ได้

**อ้างอิง:** FR-3.1–FR-3.2, FR-2.6 ใน [docs/04-requirements.md](../../04-requirements.md)  
**Milestones:** M4, M7

## Issues

| # | งาน | Owner | Phase | Branch |
|---|---|---|---|---|
| [01](issues/01-finbert-streaming.md) | FinBERT ใน Spark Structured Streaming → `news_sentiment` | M2 | PoC (T1/2569) | `feat/f3-01-finbert-streaming` |
| [02](issues/02-finbert-poc-benchmark.md) | PoC: F1 บน 100 ข่าว และ throughput | M2 | PoC (T1/2569) | `exp/f3-02-finbert-poc-benchmark` |
| [03](issues/03-goldset-300-eval.md) | Gold set 300 ข่าว: ติดป้ายแยกกัน, Cohen's kappa, Macro-F1 | M1+M2 | Full (T2/2570) | `test/f3-03-goldset-300-eval` |
| [04](issues/04-reprocess-from-raw.md) | Reprocess sentiment ทั้งหมดจาก Raw เมื่อเปลี่ยน `model_version` | M2 | PoC (T1/2569) | `feat/f3-04-reprocess-from-raw` |
