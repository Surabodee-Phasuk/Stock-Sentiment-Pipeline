# PRD: F7 — News RAG (Ask AI)

ตอบคำถามเกี่ยวกับข่าวของหุ้นในระบบพร้อมแหล่งอ้างอิง และปฏิเสธคำถามนอกขอบเขต

**อ้างอิง:** FR-6.1–FR-6.2, FR-4.4 ใน [docs/04-requirements.md](../../04-requirements.md)  
**Milestones:** M4, M6, M7

## Issues

| # | งาน | Owner | Phase | Branch |
|---|---|---|---|---|
| [01](issues/01-rag-poc.md) | PoC: ตอบ 10 คำถามพร้อมแหล่งอ้างอิง + ADR vector store | M1+M2 | PoC (T1/2569) | `exp/f7-01-rag-poc` |
| [02](issues/02-ask-ai-page.md) | หน้า Ask AI + guardrail นอกขอบเขต | M1+M2 | Full (T2/2570) | `feat/f7-02-ask-ai-page` |
| [03](issues/03-rag-eval.md) | ประเมิน 50–100 คำถาม เทียบ LLM ไม่มี RAG | M1+M2 | Full (T2/2570) | `test/f7-03-rag-eval` |
