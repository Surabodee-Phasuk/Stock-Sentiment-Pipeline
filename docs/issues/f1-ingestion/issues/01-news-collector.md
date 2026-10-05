# F1-01: News collector RSS / News API → Kafka (10 หุ้น)

**Status:** in-progress  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.1, FR-1.3  
**Branch:** `feat/f1-01-news-collector`  
**PR:** —

## งาน

- [x] `config/tickers.yaml` 10 หุ้น PoC (หลายกลุ่มอุตสาหกรรม)
- [x] collector ดึงข่าวทุก 5–15 นาที map ข่าวกับ ticker
- [x] สร้าง `news_id` = hash(URL normalize) ตาม docs/05
- [x] ส่งเข้า topic `stock-news` key = ticker (ทดสอบด้วย unit test; ยังไม่ได้ทดสอบกับ Kafka จริง — รอ INFRA-03)
- [x] บันทึก rate limit จริงของแต่ละแหล่งไว้ใน Evidence

## Acceptance criteria

- ดึงข่าวของ 10 หุ้นได้ครบ
- event ตรง schema ใน docs/05

## File scope

`ingestion/news/`, `config/`

## Evidence

- `ruff check . && ruff format --check . && pytest` ผ่าน: 31 tests (`ingestion/news/tests/`)
- รันจริง 2026-10-05 `python -m ingestion.news.collector --once --sink stdout` (Yahoo Finance RSS):
  - ครบ 10 หุ้น 185 events ใน 13.2 วินาที (delay 1 วินาที/request), HTTP 200 ทั้ง 10 request
  - ต่อหุ้น: AAPL 19, MSFT 19, NVDA 19, AMZN 19, TSLA 15, JPM 18, XOM 18, JNJ 20, KO 20, RKLB 18
  - ทุก event มี key ตรง schema docs/05 ครบ 8 ฟิลด์ ตามลำดับ
  - `news_id` ไม่ซ้ำ 169 ค่า มี 14 ข่าวที่อยู่ใน feed ของหลาย ticker
  - feed ให้ข่าวย้อนหลังประมาณ 3 วัน (published_at เก่าสุด 2026-10-02T02:35Z) และประมาณ 15–20 ข่าวต่อหุ้น
- Rate limit ของ Yahoo Finance RSS: ยิงติดกัน 50 request โดยไม่เว้นระยะ (22 วินาที) ได้ HTTP 200 ทั้งหมด ไม่เจอ 429 รอบละ 10 request ทุก 5–15 นาทีจึงต่ำกว่าขีดจำกัดมาก Yahoo ไม่ประกาศ limit อย่างเป็นทางการ จึงยังมี retry + backoff (เคารพ `Retry-After`) ไว้

## Comments
- 2026-10-05 (Claude, ขอโดย M1): ใช้ Yahoo Finance RSS เป็นแหล่งแรก (ไม่ต้องมี key) แหล่งอื่นอยู่ใน F1-03 ใส่ dependency ไว้ที่ `ingestion/news/requirements.txt` ชั่วคราวจนกว่า INFRA-04 จะมี `pyproject.toml` และเพิ่ม `ingestion/__init__.py` (นอก File scope) เพื่อให้ import `ingestion.news` ได้
- 2026-10-05 (Claude, ขอโดย M1): **ต้องตัดสินใจก่อน F2-03:** ข่าวชิ้นเดียวอยู่ได้หลาย ticker (เจอ 14/169) ถ้า `clean_news` MERGE ด้วย `news_id` อย่างเดียวจะเหลือ ticker เดียว ควรใช้ key `(news_id, ticker)` หรือแยกตาราง mapping
