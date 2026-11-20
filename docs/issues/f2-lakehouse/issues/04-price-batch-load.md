# F2-04: Spark batch: ราคาปิด → `raw_daily_price` / `daily_price`

**Status:** in-review  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.4  
**Branch:** `feat/f2-04-price-batch-load`  
**PR:** [#31](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/31)  

## งาน

- [x] โหลดผลจาก F1-02
- [x] MERGE on `ticker, trade_date`
- [x] query ตัวอย่างข่าวคู่ราคาผ่าน Athena

## Acceptance criteria

- Query ข่าวคู่กับราคาผ่าน Athena ได้

## File scope

`batch/price/`, `lakehouse/queries/`

## Evidence

รันจริง 2026-11-20 ด้วย `run-f2-04.sh` (`batch/price/load_daily_price.py`)

**1. ดึงราคาปิด (F1-02):** `rows=220 failed=-`

**2. โหลดรอบแรก**
```
input=/workspace/data/price/daily_close_*.jsonl rows=270
appended 270 rows to glue.stock_sentiment.raw_daily_price
rejected=0 unique_keys=240 inserted=240 (ที่เหลือเป็นแถวเดิมที่อัปเดตหรือข้าม)
daily_price rows=240 unique (ticker, trade_date)=240 duplicates=0 tickers=10 latest=2026-11-19
```

**3. โหลดซ้ำรอบสอง (รันซ้ำได้)**
```
input=/workspace/data/price/daily_close_*.jsonl rows=270
appended 270 rows to glue.stock_sentiment.raw_daily_price
rejected=0 unique_keys=240 inserted=0 (ที่เหลือเป็นแถวเดิมที่อัปเดตหรือข้าม)
daily_price rows=240 unique (ticker, trade_date)=240 duplicates=0 tickers=10 latest=2026-11-19
```

**4. Athena (acceptance criteria)**

| query | ผล |
|---|---|
| `daily_price` | rows=240, unique (ticker, trade_date)=240, tickers=10, latest=2026-11-19 |
| ข่าวคู่ราคา (`clean_news` JOIN `daily_price` วันเดียวกันตามเวลานิวยอร์ก) | 436 แถว จาก 10 หุ้น, engine time 891 ms (NFR-3 ≤ 5,000 ms) |

**5. โค้ด:** `ruff check .`, `ruff format --check .` ผ่าน, `pytest` 83 passed

## Comments

- 2026-11-15 (Claude, ขอโดย M1 เตรียมให้ M2): เขียน `batch/price/load_daily_price.py` และ query ข่าวคู่ราคา `lakehouse/queries/f2_04_news_with_price.sql` ทดสอบใน container กับ Iceberg catalog ชั่วคราวแล้ว: โหลดครั้งแรก 3 แถว → `daily_price` 3 คีย์, โหลดไฟล์ที่สองซ้ำวันเดิม ราคาใหม่กว่าอัปเดตแทน ส่วนราคาที่ `ingested_at` เก่ากว่าไม่ทับ, ไม่รับแถวเสีย 4 แบบตรงเหตุผล, รันซ้ำไม่เกิดแถวซ้ำ (`duplicates=0`) ค้าง: M2 รันกับตารางจริง, query ข่าวคู่ราคาใน Athena แล้วเติม Evidence และอัปเดตแถวใน BOARD ตอนเปิด PR
