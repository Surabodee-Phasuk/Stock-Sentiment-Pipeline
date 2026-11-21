# F3-04: Reprocess sentiment ทั้งหมดจาก Raw เมื่อเปลี่ยน `model_version`

**Status:** in-review  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.6  
**Branch:** `feat/f3-04-reprocess-from-raw`  
**PR:** —

## งาน

- [x] batch job อ่าน `raw_news` → เขียน `news_sentiment` ด้วย version ใหม่
- [x] ไม่ดึงข่าวจากแหล่งใหม่

## Acceptance criteria

- สาธิตได้กับข่าวชุดทดสอบ

## File scope

`batch/reprocess/`

## Evidence

**Unit test:** `pytest batch/reprocess` ผ่าน (ต้องระบุ `--model-version`, อ่าน `raw_news` เท่านั้น, ตัวกรองวันที่, ไม่ import collector / Kafka)

**สาธิตกับข่าวชุดทดสอบในเครื่อง** (PySpark 4.0 + Iceberg local, ต่อจากชุดทดสอบของ F3-01 ที่มีผล `finbert-v1` 5 แถว)

รันครั้งที่ 1 `--model-version finbert-v2`
```
raw news to reprocess: 5 unique (news_id, ticker) from local.stock_sentiment.raw_news
version=finbert-v1 rows=5 positive=1 neutral=1 negative=3 avg_score=-0.405
version=finbert-v2 rows=5 positive=1 neutral=1 negative=3 avg_score=-0.405
```
รันครั้งที่ 2 (ซ้ำ) ไม่เพิ่มแถว
```
reprocess ProsusAI/finbert as finbert-v2: scored=0 inserted=0 skipped_existing=5
```
- ผลของ `finbert-v1` ยังอยู่ครบ ทั้งสอง version อยู่คู่กันในตารางเดียว
- ใช้โมเดลเดิมจึงได้ป้ายเท่าเดิม ถ้าเปลี่ยน `--model-name` เป็นโมเดลอื่น ตารางจะเทียบผลระหว่าง version ได้ทันที

## Comments

- 2026-11-20 (M2): เพิ่ม `batch/reprocess/reprocess_sentiment.py` ใช้ขั้นตอนร่วม `sentiment/pipeline.py` จาก F3-01 สาธิตกับชุดทดสอบในเครื่องผ่าน ผ่านเกณฑ์ด้วยชุดทดสอบในเครื่อง ผลกับตารางจริงใน Glue จะเติมใน Comments หลังรัน โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
