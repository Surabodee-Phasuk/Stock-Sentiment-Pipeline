# F1-04: Backfill ข่าวและราคาปิดย้อนหลังตั้งแต่ปี 2020 สำหรับ ~50 หุ้น

**Status:** todo  
**Owner:** M1  
**Phase:** Full (T2/2570)  
**Refs:** FR-1.3, FR-1.4  
**Branch:** `feat/f1-04-backfill-2020`  
**PR:** —

## งาน

- [ ] ขยาย `config/tickers.yaml` เป็น ~50 หุ้น
- [ ] สคริปต์ backfill ราคาปิดตั้งแต่ 2020
- [ ] backfill ข่าวย้อนหลังเท่าที่แหล่งข่าวให้ได้ (บันทึกข้อจำกัด)

## Acceptance criteria

- มีราคาปิดครบ ~50 หุ้นตั้งแต่ 2020
- รายงานจำนวนข่าวย้อนหลังต่อหุ้น

## File scope

`ingestion/`, `config/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
