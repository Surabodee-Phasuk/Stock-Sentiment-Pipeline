# F1-02: Yahoo Finance daily close collector (10 หุ้น)

**Status:** done  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.2  
**Branch:** `feat/f1-02-yahoo-daily-close`  
**PR:** [#24](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/24)

## งาน

- [x] ดึงราคาปิดวันละครั้ง เว้นจังหวะระหว่างหุ้น (`--delay` 2 วินาที)
- [x] retry เมื่อโดนบล็อกชั่วคราว (429/5xx, backoff 5 → 10 → 20 วินาที)
- [x] output พร้อมให้ Spark batch อ่าน (F2-04) — JSON Lines ที่ `data/price/daily_close_<วันที่>.jsonl`

## Acceptance criteria

- ดึงราคาปิดของ 10 หุ้นได้ครบ

## File scope

`ingestion/price/`

## Evidence

รันจริง 2026-10-20 13:18 (เวลาไทย) ด้วย `python -m ingestion.price.collector --sink stdout`

```
collecting daily close for 10 tickers, last 7 days
rows=50 failed=- per_ticker={'AAPL': 5, 'MSFT': 5, 'GOOGL': 5, 'AMZN': 5, 'NVDA': 5, 'META': 5, 'TSLA': 5, 'AVGO': 5, 'RKLB': 5, 'SPCX': 5}
latest={... ทุกตัว: '2026-10-19'}
source_stats=SourceStats(requests=10, retries=0, failures=0, status_counts={200: 10})
```
- ครบ 10 หุ้น หุ้นละ 5 วันทำการ (13–16 และ 19 ต.ค.) ใช้เวลา 19.8 วินาที ไม่โดน rate limit
- ราคาปิด 2026-10-19 ตัวอย่าง: AAPL 342.94, NVDA 217.09, TSLA 368.06, RKLB 51.36, SPCX 147.96
- `ruff check .`, `ruff format --check .` ผ่าน, `pytest` 44 passed (ของใหม่ 13 กรณีใน `ingestion/price/tests/`)

## Comments

- 2026-10-20 (Claude, ขอโดย M1): ใช้ Yahoo chart API (`/v8/finance/chart`) ตรงด้วย urllib แทน yfinance เพื่อไม่ต้องลง pandas และทดสอบด้วย fixture ได้ (endpoint เดียวกับ yfinance ความเสี่ยงใน docs/09 ยังเหมือนเดิม) ดึงย้อนหลัง 7 วันทุกรอบ ไม่เอาแท่งของวันที่ตลาดยังเปิด และ `trade_date` ใช้วันตามเวลานิวยอร์ก
- 2026-10-25 (Claude, ขอโดย M1): PR #24 merge เข้า `main` แล้ว ปิด issue
