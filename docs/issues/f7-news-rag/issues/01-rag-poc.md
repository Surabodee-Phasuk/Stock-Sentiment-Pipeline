# F7-01: PoC: ตอบ 10 คำถามพร้อมแหล่งอ้างอิง + ADR vector store

**Status:** todo  
**Owner:** M1+M2  
**Phase:** Full (T2/2570)  
**Refs:** FR-6.1, FR-6.2  
**Branch:** `exp/f7-01-rag-poc`  
**PR:** —

## งาน

- [ ] index ข่าวชั้น Cleaned
- [ ] retrieval กรองตาม ticker
- [ ] 10 คำถามทดสอบ
- [ ] ADR embedding / vector store

## Acceptance criteria

- ตอบ 10 คำถามทดสอบได้

## File scope

`ai/rag/`, `docs/adr/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments

- 2026-10-12 (M1): เลื่อน PoC นี้ไปเทอม 2 — เทอม 1 โฟกัส pipeline, Lakehouse และ FinBERT ยังไม่แตะ RAG
