# F2-04: Spark batch: ราคาปิด → `raw_daily_price` / `daily_price`

**Status:** todo  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.4  
**Branch:** `feat/f2-04-price-batch-load`  
**PR:** —

## งาน

- [ ] โหลดผลจาก F1-02
- [ ] MERGE on `ticker, trade_date`
- [ ] query ตัวอย่างข่าวคู่ราคาผ่าน Athena

## Acceptance criteria

- Query ข่าวคู่กับราคาผ่าน Athena ได้

## File scope

`batch/price/`, `lakehouse/queries/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
