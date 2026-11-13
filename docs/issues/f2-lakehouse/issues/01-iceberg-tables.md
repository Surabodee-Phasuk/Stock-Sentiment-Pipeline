# F2-01: DDL ตาราง Iceberg ทั้งสามชั้นใน Glue

**Status:** in-review  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.1  
**Branch:** `feat/f2-01-iceberg-tables`  
**PR:** [#26](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/26)

## งาน

- [x] DDL ตาม docs/05 ใน `lakehouse/ddl/` (6 ตาราง: `01_raw_news.sql` … `06_sentiment_daily.sql`)
- [x] สร้างตารางผ่านสคริปต์ที่รันซ้ำได้ (`lakehouse/ddl/create_tables.py`, ทุกไฟล์ใช้ `CREATE TABLE IF NOT EXISTS`)

## Acceptance criteria

- ทุกตารางเห็นใน Athena

## File scope

`lakehouse/`

## Evidence

รันจริง 2026-11-06 (`surabodee-dev` ใช้สิทธิ์ `StockSentimentDev` เท่านั้น)

**1. สร้างตารางใน Glue:** `spark-submit lakehouse/ddl/create_tables.py`
```
created glue.stock_sentiment.raw_news  (01_raw_news.sql)
created glue.stock_sentiment.raw_daily_price  (02_raw_daily_price.sql)
created glue.stock_sentiment.clean_news  (03_clean_news.sql)
created glue.stock_sentiment.news_sentiment  (04_news_sentiment.sql)
created glue.stock_sentiment.daily_price  (05_daily_price.sql)
created glue.stock_sentiment.sentiment_daily  (06_sentiment_daily.sql)
  raw_news: 13 columns, partition ['days(published_at)']
  raw_daily_price: 6 columns, partition ['years(trade_date)']
  clean_news: 9 columns, partition ['days(published_at)']
  news_sentiment: 8 columns, partition ['days(published_at)']
  daily_price: 6 columns, partition ['years(trade_date)']
  sentiment_daily: 14 columns, partition ['years(trade_date)']
all 6 tables ready in glue.stock_sentiment
```

**2. รันซ้ำได้:** รันรอบสองขึ้น `exists` ครบ 6 ตาราง และจบด้วย `all 6 tables ready`

**3. เห็นใน Athena (acceptance criteria):** workgroup `stock-sentiment` แสดง Tables (6) และ query นับแถวทั้ง 6 ตารางสำเร็จ (`Completed`) ได้ 0 ทุกตาราง เพราะยังไม่มีข้อมูล

**4. เป็น Iceberg:** `aws glue get-tables --database-name stock_sentiment`
```
clean_news       ICEBERG
daily_price      ICEBERG
news_sentiment   ICEBERG
raw_daily_price  ICEBERG
raw_news         ICEBERG
sentiment_daily  ICEBERG
```

**5. โค้ด:** `ruff check .`, `ruff format --check .` ผ่าน, `pytest` 59 passed (ใหม่ 10 กรณีใน `lakehouse/tests/`)

## Comments

- 2026-10-27 (Claude, ขอโดย M1): เขียน DDL 6 ตาราง + สคริปต์สร้างตาราง + unit test (`--dry-run` ไม่ต้องใช้ Spark) เติมคอลัมน์ของ `raw_news`, `clean_news`, `raw_daily_price`, `daily_price` ใน docs/05 และบันทึกคีย์ `clean_news` = `(news_id, ticker)` ใน ADR-0007 เพิ่ม `published_at` ใน `news_sentiment` (ใช้ partition) และ `computed_at` ใน `sentiment_daily` ค้าง: รันสร้างตารางจริงบน Glue แล้วเช็กใน Athena (acceptance criteria) แล้วเติม Evidence
- 2026-11-06 (Claude, ขอโดย M1): สร้างตารางจริงแล้ว ผ่านเกณฑ์ ข้อควรรู้: Athena รัน `SHOW CREATE TABLE` กับตารางเหล่านี้ไม่ได้ (`table has unsupported properties`) แต่อ่านตารางได้ปกติ จึงเช็กชนิดตารางจาก Glue แทน
