# F2-02: Spark Structured Streaming: Kafka → `raw_news` พร้อม checkpoint

**Status:** todo  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.2, NFR-1, NFR-2  
**Branch:** `feat/f2-02-kafka-to-raw-streaming`  
**PR:** —

## งาน

- [ ] อ่าน topic `stock-news`
- [ ] append ลง `raw_news` checkpoint บน S3
- [ ] วัดเวลา published_at → เขียนลงตาราง

## Acceptance criteria

- ข่าวใหม่ปรากฏในตารางภายใน 15 นาที

## File scope

`streaming/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
