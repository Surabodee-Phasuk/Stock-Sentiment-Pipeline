# F2-03: ตัดข่าวซ้ำ: `raw_news` → `clean_news` ด้วย MERGE

**Status:** todo  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.3, NFR-4  
**Branch:** `feat/f2-03-dedup-to-cleaned`  
**PR:** —

## งาน

- [ ] MERGE on `news_id`
- [ ] validation: field ว่าง, timestamp ผิดปกติ, ticker นอก config

## Acceptance criteria

- duplicate rate ในชั้น Cleaned = 0% (query ใน Evidence)

## File scope

`streaming/`, `lakehouse/queries/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
