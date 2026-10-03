# F1-02: Yahoo Finance daily close collector (10 หุ้น)

**Status:** todo  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.2  
**Branch:** `feat/f1-02-yahoo-daily-close`  
**PR:** —

## งาน

- [ ] ดึงราคาปิดวันละครั้ง เว้นจังหวะระหว่างหุ้น
- [ ] retry เมื่อโดนบล็อกชั่วคราว
- [ ] output พร้อมให้ Spark batch อ่าน (F2-04)

## Acceptance criteria

- ดึงราคาปิดของ 10 หุ้นได้ครบ

## File scope

`ingestion/price/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
