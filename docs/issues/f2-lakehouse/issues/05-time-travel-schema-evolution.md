# F2-05: สาธิต time travel และ schema evolution

**Status:** done  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.5  
**Branch:** `exp/f2-05-time-travel-schema-evolution`  
**PR:** [#29](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/29)

## งาน

- [x] notebook/สคริปต์สาธิต query ณ snapshot ก่อนหน้า (`lakehouse/demo/time_travel_schema_evolution.py`)
- [x] เพิ่มคอลัมน์ใหม่โดยไม่เขียนข้อมูลเก่าใหม่

## Acceptance criteria

- สาธิตได้กับข่าวชุดทดสอบ

## File scope

`lakehouse/demo/`

## Evidence

รันจริง 2026-11-15 ด้วย `lakehouse/demo/time_travel_schema_evolution.py` (สิทธิ์ `StockSentimentDev`)

**A. time travel กับ `raw_news` จริง (อ่านอย่างเดียว)**
- มี 30 snapshot ตั้งแต่ 2026-11-06 09:13 UTC (ทุกครั้งที่ Spark Streaming เขียน = 1 snapshot)
```
rows at first snapshot (VERSION AS OF 1192482071043151478) = 284
rows at '2026-11-06 09:13:36.744' UTC (TIMESTAMP AS OF)     = 284
rows now                                                    = 696
```

**B. ตารางสาธิต `zz_f205_demo` (ข่าวจริงจาก raw, ลบทิ้งตอนจบ)**

| ขั้น | ผล |
|---|---|
| B1–B3 insert 30 + 10 แล้วลบ TSLA | 30 → 40 → 33 (ลบ 7) |
| B4 time travel ทุกเวอร์ชัน | v1 rows=30 TSLA=7 · v2 rows=40 TSLA=7 · v3 rows=33 TSLA=0 |
| B5 schema evolution: เพิ่ม `sentiment_hint`, เปลี่ยนชื่อ `headline` → `title` | data files 6 → 6, snapshots 3 → 3 (ไม่เขียนไฟล์เก่าใหม่) แถวเก่า 33 แถวมี `sentiment_hint` เป็น NULL |
| B5 schema ตามเวอร์ชัน | ปัจจุบัน `[news_id, ticker, title, source, published_at, sentiment_hint]` · v1 `[news_id, ticker, headline, source, published_at]` |
| B6 rollback ไป v2 | rows=40 TSLA=7 กลับมาเท่ากับ v2 |

`ruff check .`, `ruff format --check .` ผ่าน, `pytest` 77 passed

ข้อควรรู้: log ตอนเริ่ม Spark อาจขึ้น `NullPointerException ... BlockManagerId` เป็น error ภายในของ Spark local mode ตอนเริ่มต้น ไม่กระทบผล (สาธิตรันจบ `demo finished`)

## Comments

- 2026-11-15 (M1): เขียนสคริปต์สาธิตและ query Athena ทดสอบใน container กับ Iceberg catalog ชั่วคราว: time travel ทั้ง `VERSION AS OF` และ `TIMESTAMP AS OF` ได้จำนวนแถวตรงทุกเวอร์ชัน (v1=30, v2=40, v3=30 หลังลบ TSLA), เพิ่มและเปลี่ยนชื่อคอลัมน์แล้ว data files 1 → 1 และไม่มี snapshot ใหม่, เวอร์ชันเก่ายังเห็น schema เดิม, rollback กลับ v2 ได้ ค้าง: รันกับ `raw_news` จริงแล้วเติม Evidence
