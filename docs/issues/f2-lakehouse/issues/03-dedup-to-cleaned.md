# F2-03: ตัดข่าวซ้ำ: `raw_news` → `clean_news` ด้วย MERGE

**Status:** in-review  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.3, NFR-4  
**Branch:** `feat/f2-03-dedup-to-cleaned`  
**PR:** —

## งาน

- [x] MERGE on `news_id, ticker` (ADR-0007)
- [x] validation: field ว่าง, timestamp ผิดปกติ, ticker นอก config

## Acceptance criteria

- duplicate rate ในชั้น Cleaned = 0% (query ใน Evidence)

## File scope

`streaming/`, `lakehouse/queries/`

## Evidence

รันจริง 2026-11-15 กับ `glue.stock_sentiment` (สิทธิ์ `StockSentimentDev`)

**1. `clean_news_job.py --once`**
```
batch=0 raw_rows=696 rejected=0 unique_keys=439 inserted=439 already_in_clean=0
clean_news rows=439 unique (news_id, ticker)=439 duplicates=0 duplicate_rate=0.00%
```

**2. Athena (`lakehouse/queries/f2_03_duplicate_rate.sql`) — acceptance criteria**

| query | ผล |
|---|---|
| duplicate rate ของ `clean_news` | rows=439, unique_keys=439, **duplicates=0** |
| เทียบชั้น | `raw_news` 696 แถว / 439 คีย์ → `clean_news` 439 แถว / 439 คีย์ (ตัดซ้ำ 257 แถว) |
| ข่าวต่อหุ้น | ครบ 10 หุ้น: AAPL 50, AMZN 44, AVGO 36, GOOGL 45, META 37, MSFT 51, NVDA 82, RKLB 20, SPCX 30, TSLA 44 (รวม 439) |

**3. ทดสอบกรณีขอบใน container** (Iceberg catalog ชั่วคราว ไม่แตะ AWS)
- ข้อมูล 11 แถว: ไม่รับ 5 แถวตรงเหตุผล (`missing_field` 2, `bad_timestamp` 2, `unknown_ticker` 1) ได้ 3 คีย์
- รันซ้ำไม่เพิ่มแถว, เพิ่มข่าวซ้ำ 1 + ข่าวใหม่ 1 แล้วเพิ่มเฉพาะข่าวใหม่ (`inserted=1 already_in_clean=1`)
- ข่าวเดียวกันคนละหุ้นเก็บแยกแถว (ADR-0007) ข่าวที่เจอหลายแหล่งเก็บแหล่งแรก

**4. โค้ด:** `ruff check .`, `ruff format --check .` ผ่าน, `pytest` 73 passed

## Comments

- 2026-11-15 (Claude, ขอโดย M1): เขียน `streaming/clean_news_job.py` อ่าน `raw_news` แบบ streaming แล้ว MERGE ลง `clean_news` เฉพาะคีย์ที่ยังไม่มี ตรวจ 3 ข้อ: ฟิลด์ว่าง (`news_id`, `ticker`, `headline`, `url`), เวลาผิดปกติ (`published_at` ว่าง ก่อนปี 2000 หรือเกินเวลาที่โหลด 1 ชั่วโมง), ticker ไม่อยู่ใน `config/tickers.yaml` ค้าง: ทดสอบใน container แล้วรันกับตารางจริง และ query duplicate rate ใน Athena
- 2026-11-15 (Claude, ขอโดย M1): ทดสอบใน container กับ Iceberg catalog ชั่วคราว ข้อมูลทดสอบ 11 แถว: ซ้ำ 3 แบบ, ฟิลด์ว่าง 2, เวลาผิด 2, ticker นอก config 1 → ไม่รับ 5 แถวตรงเหตุผล, ได้ 3 คีย์, `duplicate_rate=0.00%` รันซ้ำไม่มีอะไรเพิ่ม และเพิ่มข่าวซ้ำกับข่าวใหม่แล้วเพิ่มเฉพาะข่าวใหม่ (inserted=1, already_in_clean=1) ข่าวที่เจอหลายแหล่งเก็บแหล่งแรก ค้าง: รันกับตารางจริงแล้วเติม Evidence
