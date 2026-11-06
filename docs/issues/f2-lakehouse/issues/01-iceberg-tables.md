# F2-01: DDL ตาราง Iceberg ทั้งสามชั้นใน Glue

**Status:** in-progress  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.1  
**Branch:** `feat/f2-01-iceberg-tables`  
**PR:** —

## งาน

- [x] DDL ตาม docs/05 ใน `lakehouse/ddl/` (6 ตาราง: `01_raw_news.sql` … `06_sentiment_daily.sql`)
- [x] สร้างตารางผ่านสคริปต์ที่รันซ้ำได้ (`lakehouse/ddl/create_tables.py`, ทุกไฟล์ใช้ `CREATE TABLE IF NOT EXISTS`)

## Acceptance criteria

- ทุกตารางเห็นใน Athena

## File scope

`lakehouse/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments

- 2026-10-27 (Claude, ขอโดย M1): เขียน DDL 6 ตาราง + สคริปต์สร้างตาราง + unit test (`--dry-run` ไม่ต้องใช้ Spark) เติมคอลัมน์ของ `raw_news`, `clean_news`, `raw_daily_price`, `daily_price` ใน docs/05 และบันทึกคีย์ `clean_news` = `(news_id, ticker)` ใน ADR-0007 เพิ่ม `published_at` ใน `news_sentiment` (ใช้ partition) และ `computed_at` ใน `sentiment_daily` ค้าง: รันสร้างตารางจริงบน Glue แล้วเช็กใน Athena (acceptance criteria) แล้วเติม Evidence
