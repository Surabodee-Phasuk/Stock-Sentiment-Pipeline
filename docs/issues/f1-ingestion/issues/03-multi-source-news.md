# F1-03: รวมหลายแหล่งข่าวและตัดซ้ำเบื้องต้นที่ collector

**Status:** in-review  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.5  
**Branch:** `feat/f1-03-multi-source-news`  
**PR:** —

## งาน

- [x] เพิ่มแหล่งข่าวอย่างน้อย 2 แหล่ง (Yahoo + Nasdaq RSS, `--sources`)
- [x] normalize URL ก่อน hash (ทำไว้แล้วใน F1-01 `normalize_url`; F1-03 เพิ่มการทดสอบข้ามแหล่ง)

## Acceptance criteria

- ข่าวเดียวกันจากหลายแหล่งได้ `news_id` เดียวกันเมื่อ URL ตรงกัน

## File scope

`ingestion/news/`

## Evidence

รันจริง 2026-10-25 ด้วย `python -m ingestion.news.collector --once --sink stdout`

```
fetched=311 sent=311 skipped_seen=0 failed=-
per_ticker={'AAPL': 34, 'MSFT': 33, 'GOOGL': 35, 'AMZN': 33, 'NVDA': 34, 'META': 34, 'TSLA': 33, 'AVGO': 33, 'RKLB': 20, 'SPCX': 22}
source_stats={'rss:yahoo': requests=10 failures=0 {200: 10}, 'rss:nasdaq': requests=10 failures=0 {200: 10}}
```
- แยกตามแหล่ง: yahoo 187, nasdaq 124 ไม่มีแหล่งไหนโดน rate limit
- ซ้ำข้ามแหล่งในรอบจริง 0 เรื่อง (Yahoo ลิงก์เว็บต้นทาง, Nasdaq ลิงก์ nasdaq.com) เกณฑ์ news_id เดียวกันพิสูจน์ด้วย fixture: `test_same_article_from_two_sources_gets_same_news_id`
- `ruff check .`, `ruff format --check .` ผ่าน, `pytest` 49 passed (ใหม่ 5 กรณี)

## Comments

- 2026-10-25 (Claude, ขอโดย M1): เลือก Nasdaq RSS เป็นแหล่งที่สอง (RSS 2.0 ใช้ `parse_rss` เดิมได้) ตัด Seeking Alpha (link เป็นหน้า symbol เดียวกันทุก item ทำให้ news_id ชน) และ Google News (link เป็น redirect) แยกคลาสฐาน `TickerRssSource` ให้เพิ่มแหล่งใหม่ได้ด้วย `name` + `url_template`
