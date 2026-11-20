# F2-04: Spark batch: ราคาปิด → `raw_daily_price` / `daily_price`

**Status:** in-progress  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.4  
**Branch:** `feat/f2-04-price-batch-load`  
**PR:** —

## งาน

- [x] โหลดผลจาก F1-02
- [x] MERGE on `ticker, trade_date`
- [ ] query ตัวอย่างข่าวคู่ราคาผ่าน Athena

## Acceptance criteria

- Query ข่าวคู่กับราคาผ่าน Athena ได้

## File scope

`batch/price/`, `lakehouse/queries/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments

- 2026-11-15 (Claude, ขอโดย M1 เตรียมให้ M2): เขียน `batch/price/load_daily_price.py` และ query ข่าวคู่ราคา `lakehouse/queries/f2_04_news_with_price.sql` ทดสอบใน container กับ Iceberg catalog ชั่วคราวแล้ว: โหลดครั้งแรก 3 แถว → `daily_price` 3 คีย์, โหลดไฟล์ที่สองซ้ำวันเดิม ราคาใหม่กว่าอัปเดตแทน ส่วนราคาที่ `ingested_at` เก่ากว่าไม่ทับ, ไม่รับแถวเสีย 4 แบบตรงเหตุผล, รันซ้ำไม่เกิดแถวซ้ำ (`duplicates=0`) ค้าง: M2 รันกับตารางจริง, query ข่าวคู่ราคาใน Athena แล้วเติม Evidence และอัปเดตแถวใน BOARD ตอนเปิด PR
