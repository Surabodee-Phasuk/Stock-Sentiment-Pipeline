# F5-02: Stock Detail PoC ดึงข้อมูลจริงจาก Athena

**Status:** in-review  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-4.3  
**Branch:** `feat/f5-02-stock-detail-real-data`  
**PR:** [#36](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/36)  

## งาน

- [x] API ดึงข้อมูลจริงจาก Athena: สรุป 24 ชม., ราคาปิด, sentiment รายวันคู่ราคาปิด
- [x] หน้า Stock Detail แสดงข่าวล่าสุดพร้อมแหล่ง/label/score จาก API
- [ ] ทดสอบกับ Athena จริง (ต้องมีข้อมูลใน `news_sentiment` จาก F3-01 ก่อน)

กราฟ sentiment vs ราคาปิดย้ายไป [F5-05](05-stock-detail-full.md) (เทอม 2) ตาม ADR-0008

## Acceptance criteria

- หน้า Stock Detail ดึงข้อมูลจริงได้

## File scope

`webapp/`

## Evidence

**API** `GET /api/stock/{ticker}?days=30` รวม 3 query Athena ที่รันพร้อมกัน (sentiment รายวันคู่ราคาปิด, ข่าวล่าสุดพร้อมป้าย/score, สรุป 24 ชม.) cache 5 นาที
- sentiment รายวันคู่ราคาปิด (`daily`): `avg(sentiment_score)` ต่อวันตามเวลานิวยอร์ก กับ `close` จาก `daily_price` เตรียมไว้ให้กราฟใน F5-05
- ข่าวล่าสุด: headline, แหล่ง, เวลา, ป้าย, score จาก `news_sentiment` JOIN `clean_news`
- ticker นอกระบบ → 404, Athena ล้ม → 503, ค่าใน SQL ผ่านการตรวจ (กัน SQL injection)

**Unit test:** `pytest webapp` 19 passed (แปลงผล Athena, รอ query/ล้ม/timeout, รูปข้อมูลตรงกับหน้าเว็บ, cache, 404, 503)

**ทดสอบหน้าเว็บกับ Athena จำลอง:** หน้า `/stock/NVDA` แสดงภาพรวม ราคาปิด ข่าว และป้าย "ข้อมูลจริง · Athena" ครบ

**กับ Athena จริง:** _(รันหลังมีข้อมูลใน `news_sentiment` และ `daily_price` แล้ว: `uvicorn webapp.api.main:app` → เปิด `/stock/NVDA` แคปหน้าจอ และจด `query_seconds` จาก `/api/stock/NVDA`)_

## Comments

- 2026-11-20 (M2): เพิ่ม `webapp/api/athena.py` และ `/api/stock/{ticker}` หน้า Stock Detail เปลี่ยนจากข้อมูลตัวอย่างเป็น API จริง ทดสอบกับ Athena จำลองผ่าน รอทดสอบกับ Athena จริง
- 2026-11-24 (M1): ปรับก่อนเปิด PR ให้ตรงกับ F5-01 และ ADR-0008: ย้ายกราฟไป F5-05, ข้อความแหล่งข้อมูลเป็นภาษาไทย, error จาก boto3 (ไม่มี credential / ไม่มีสิทธิ์ / เครือข่าย) ตอบ 503 ตามที่ README ระบุ และหน้าเว็บมีลิงก์ดูข้อมูลตัวอย่างเมื่อโหลดไม่สำเร็จ ยังค้างการทดสอบกับ Athena จริง
