# F1-01: News collector RSS / News API → Kafka (10 หุ้น)

**Status:** todo  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.1, FR-1.3  
**Branch:** `feat/f1-01-news-collector`  
**PR:** —

## งาน

- [ ] `config/tickers.yaml` 10 หุ้น PoC (หลายกลุ่มอุตสาหกรรม)
- [ ] collector ดึงข่าวทุก 5–15 นาที map ข่าวกับ ticker
- [ ] สร้าง `news_id` = hash(URL normalize) ตาม docs/05
- [ ] ส่งเข้า topic `stock-news` key = ticker
- [ ] บันทึก rate limit จริงของแต่ละแหล่งไว้ใน Evidence

## Acceptance criteria

- ดึงข่าวของ 10 หุ้นได้ครบ
- event ตรง schema ใน docs/05

## File scope

`ingestion/news/`, `config/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
