# F3-01: FinBERT ใน Spark Structured Streaming → `news_sentiment`

**Status:** in-review  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-3.1  
**Branch:** `feat/f3-01-finbert-streaming`  
**PR:** —

## งาน

- [x] wrapper FinBERT ใน `sentiment/`
- [x] เรียกจาก streaming job เขียน label, score, `model_version`

## Acceptance criteria

- ข่าวใหม่มีผล sentiment ในตาราง

## File scope

`sentiment/`, `streaming/`

## Evidence

**Unit test:** `pytest sentiment streaming` ผ่าน (wrapper, การสร้าง input, score, คีย์ MERGE, คอลัมน์ตรงกับ DDL)

**ทดสอบ end-to-end ในเครื่อง** (PySpark 4.0 + Iceberg 1.12 local catalog, โมเดล `ProsusAI/finbert` จริง ไม่แตะ AWS)

รอบ 1: ใส่ raw 7 แถว = ข่าวดี (ซ้ำ 2 แหล่ง), ข่าวร้าย, ข่าวเดียวสองหุ้น (AAPL, MSFT), ticker นอกระบบ, headline ว่าง
```
batch=0 scored=4 inserted=4 positive=1 neutral=0 negative=3
news_sentiment[finbert-v1] rows=4 unique (news_id, ticker)=4 duplicates=0
```
รอบ 2: ส่งข่าว TSLA เดิมซ้ำ + ข่าวใหม่ 1 ข่าว
```
batch=1 scored=1 inserted=1 positive=0 neutral=1 negative=0
news_sentiment[finbert-v1] rows=5 unique (news_id, ticker)=5 duplicates=0
```
| news_id | ticker | sentiment | score |
|---|---|---|---|
| n1 | NVDA | positive | 0.826 |
| n2 | TSLA | negative | -0.955 |
| n3 | AAPL | negative | -0.944 |
| n3 | MSFT | negative | -0.944 |
| n6 | AMZN | neutral | -0.011 |

- ข่าวซ้ำและข่าวที่มีผลแล้วไม่ถูกส่งเข้าโมเดลซ้ำ ticker นอกระบบและ headline ว่างถูกตัดตามกฎ F2-03

## Comments

- 2026-11-20 (M2): เพิ่ม `sentiment/finbert.py`, `sentiment/pipeline.py`, `streaming/news_sentiment_job.py` และ service `spark-ml` (`infra/spark/Dockerfile.ml`, นอก File scope เพราะ image เดิมไม่มี torch) ทดสอบ end-to-end ในเครื่องผ่าน ผ่านเกณฑ์ด้วยชุดทดสอบในเครื่อง ผลกับตารางจริงใน Glue จะเติมใน Comments หลังรัน โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
