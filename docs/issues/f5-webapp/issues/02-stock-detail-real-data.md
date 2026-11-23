# F5-02: Stock Detail PoC ดึงข้อมูลจริงจาก Athena

**Status:** in-progress  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-4.3  
**Branch:** `feat/f5-02-stock-detail-real-data`  
**PR:** —

## งาน

- [x] กราฟ sentiment vs ราคาปิด
- [x] ข่าวล่าสุดพร้อมแหล่ง/label/score

## Acceptance criteria

- หน้า Stock Detail ดึงข้อมูลจริงได้

## File scope

`webapp/`

## Evidence

**API** `GET /api/stock/{ticker}?days=30` รวม 3 query Athena ที่รันพร้อมกัน (sentiment รายวันคู่ราคาปิด, ข่าวล่าสุดพร้อมป้าย/score, สรุป 24 ชม.) cache 5 นาที
- กราฟ sentiment vs ราคาปิด: แท่ง = `avg(sentiment_score)` รายวัน (วันตามเวลานิวยอร์ก), เส้น = `close` จาก `daily_price`
- ข่าวล่าสุด: headline, แหล่ง, เวลา, ป้าย, score จาก `news_sentiment` JOIN `clean_news`
- ticker นอกระบบ → 404, Athena ล้ม → 503, ค่าใน SQL ผ่านการตรวจ (กัน SQL injection)

**Unit test:** `pytest webapp` 19 passed (แปลงผล Athena, รอ query/ล้ม/timeout, รูปข้อมูลตรงกับหน้าเว็บ, cache, 404, 503)

**ทดสอบหน้าเว็บกับ Athena จำลอง:** หน้า `/stock/NVDA` แสดงกราฟ ข่าว และป้าย "ข้อมูลจริง · Athena" ครบ

**กับ Athena จริง:** _(รันหลังมีข้อมูลใน `news_sentiment` และ `daily_price` แล้ว: `uvicorn webapp.api.main:app` → เปิด `/stock/NVDA` แคปหน้าจอ และจด `query_seconds` จาก `/api/stock/NVDA`)_

## Comments

- 2026-11-20 (M2): เพิ่ม `webapp/api/athena.py` และ `/api/stock/{ticker}` หน้า Stock Detail เปลี่ยนจากข้อมูลตัวอย่างเป็น API จริง ทดสอบกับ Athena จำลองผ่าน รอทดสอบกับ Athena จริง โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
