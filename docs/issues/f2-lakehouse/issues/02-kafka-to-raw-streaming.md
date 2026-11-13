# F2-02: Spark Structured Streaming: Kafka → `raw_news` พร้อม checkpoint

**Status:** in-review  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.2, NFR-1, NFR-2  
**Branch:** `feat/f2-02-kafka-to-raw-streaming`  
**PR:** [#27](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/27)

## งาน

- [x] อ่าน topic `stock-news`
- [x] append ลง `raw_news` checkpoint บน S3
- [x] วัดเวลา published_at → เขียนลงตาราง

## Acceptance criteria

- ข่าวใหม่ปรากฏในตารางภายใน 15 นาที

## File scope

`streaming/`

## Evidence

รันจริง 2026-11-06 กับ `glue.stock_sentiment.raw_news` และ checkpoint บน S3 (สิทธิ์ `StockSentimentDev`)

**1. ข่าวจริงลงตาราง:** `raw_news_stream.py --once` ได้ `batch=0 rows=284` แล้วรันต่อเนื่องอ่านต่อจาก checkpoint

**2. วัดเวลา:** `check_raw_news.py` หลัง collector รันทุก 5 นาที รวม 21 รอบ (ประมาณ 18:19 น. เวลาไทย ก่อนตลาดสหรัฐฯ เปิด)
```
rows=625  unreadable_rows=0  unique (news_id, ticker)=368
collector rounds=21  fresh news=54
collector->table (pipeline): p50=50s  p95=59s    max=60s    within_15min=54/54
published->collector (feed): p50=867s p95=10039s max=45823s within_15min=29/54
published->table (รวม):      p50=912s p95=10080s max=45855s within_15min=26/54
```

**สรุปกับเกณฑ์:** ยังไม่ผ่านเมื่อวัดจาก `published_at` (26/54) ส่วนที่ pipeline ควบคุมได้ใช้เวลาไม่เกิน 60 วินาที (54/54) เวลาที่เกินเกิดก่อนข่าวถึง collector รอบดึงเพิ่มได้ไม่เกิน 5 นาที แต่ข่าวช้าสุดเจอหลังเวลาเผยแพร่ประมาณ 12.7 ชั่วโมง จึงชี้ว่าข่าวบางชิ้นเข้า feed ช้า ยังไม่ได้แยกตามแหล่ง และวัดนอกเวลาตลาด รอคุยเกณฑ์กับอาจารย์ และวัดซ้ำใน QA-01

**3. โค้ด:** `ruff check .`, `ruff format --check .` ผ่าน, `pytest` 57 passed บน branch นี้

## Comments

- 2026-11-06 (Claude, ขอโดย M1): เขียน `streaming/raw_news_stream.py` และ `check_raw_news.py` ทดสอบใน container กับ Iceberg catalog ชั่วคราวแล้ว: อ่านได้ 284 ข่าว รันซ้ำจาก checkpoint ได้ 0 แถวใหม่ ไม่เขียนซ้ำ เพิ่ม `hadoop-aws` ใน `infra/spark/spark-defaults.conf` เพราะ checkpoint บน S3 ต้องใช้ `s3a://` ค้าง: รันกับ `raw_news` จริงบน S3, วัดเวลาว่าไม่เกิน 15 นาที แล้วเติม Evidence
- 2026-11-06 (Claude, ขอโดย M1): `rows` มากกว่า `unique` เพราะ collector ที่เปิดใหม่ส่งข่าวเดิมซ้ำ เป็นเรื่องปกติของ Raw และ F2-03 จะตัดซ้ำ
