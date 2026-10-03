# F3-04: Reprocess sentiment ทั้งหมดจาก Raw เมื่อเปลี่ยน `model_version`

**Status:** todo  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.6  
**Branch:** `feat/f3-04-reprocess-from-raw`  
**PR:** —

## งาน

- [ ] batch job อ่าน `raw_news` → เขียน `news_sentiment` ด้วย version ใหม่
- [ ] ไม่ดึงข่าวจากแหล่งใหม่

## Acceptance criteria

- สาธิตได้กับข่าวชุดทดสอบ

## File scope

`batch/reprocess/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
