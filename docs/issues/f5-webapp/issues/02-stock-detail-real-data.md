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
- [x] ทดสอบกับ Athena จริง

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

**Unit test:** `pytest` 131 passed, 0 skipped (เฉพาะ `webapp` 22) ใน environment ที่ติดตั้งกลุ่ม `web` (แปลงผล Athena, รอ query/ล้ม/timeout, รูปข้อมูลตรงกับหน้าเว็บ, cache, 404, 503)

**ทดสอบหน้าเว็บกับ Athena จำลอง:** หน้า `/stock/NVDA` แสดงภาพรวม ราคาปิด ข่าว และป้าย "ข้อมูลจริง · Athena" ครบ

**กับ Athena จริง** (2026-11-24 เวลาไทย, workgroup `stock-sentiment`, region Sydney)

| ตาราง | แถว | หมายเหตุ |
|---|---|---|
| `clean_news` | 729 | 10 หุ้น, ซ้ำ 0% |
| `news_sentiment` (`finbert-v1`) | 729 | คีย์ `(news_id, ticker)` ไม่ซ้ำ ครบทุกข่าวใน `clean_news` (negative 254, neutral 220, positive 255) |
| `daily_price` | 260 | 10 หุ้น, ล่าสุด 2026-11-23, ซ้ำ 0 |

- `GET /api/stock/{ticker}` ตอบ 200 ครบ 10 หุ้น หุ้นละ 12 ข่าว `query_seconds` 2.08–3.49 (3 query พร้อมกัน) เรียกซ้ำจาก cache 0.003 s, ticker นอกระบบ (`ZZZZ`) ตอบ 404
- NVDA: ราคาปิด 165.05 (2026-11-23) ตรงกับไฟล์จาก Yahoo Finance, ข่าว 24 ชม. 29 ข่าว (positive 12, neutral 10, negative 7), รอบที่ถ่ายภาพ `query_seconds` 3.91
- หน้า `/stock/NVDA` และ `/stock/TSLA` แสดงภาพรวม ราคาปิด ข่าว และ "ข้อมูลจริง · Athena" (ภาพใน PR)

## Comments

- 2026-11-20 (M2): เพิ่ม `webapp/api/athena.py` และ `/api/stock/{ticker}` หน้า Stock Detail เปลี่ยนจากข้อมูลตัวอย่างเป็น API จริง ทดสอบกับ Athena จำลองผ่าน รอทดสอบกับ Athena จริง
- 2026-11-24 (M1): ปรับก่อนเปิด PR ให้ตรงกับ F5-01 และ ADR-0008: ย้ายกราฟไป F5-05, ข้อความแหล่งข้อมูลเป็นภาษาไทย, error จาก boto3 (ไม่มี credential / ไม่มีสิทธิ์ / เครือข่าย) ตอบ 503 ตามที่ README ระบุ และหน้าเว็บมีลิงก์ดูข้อมูลตัวอย่างเมื่อโหลดไม่สำเร็จ ยังค้างการทดสอบกับ Athena จริง
- 2026-11-24 (M1): รัน pipeline หนึ่งรอบบน AWS (ข่าวใหม่ 290 คีย์, ราคาใหม่ 20 แถว, FinBERT 729 ข่าว) แล้วทดสอบหน้าเว็บกับ Athena จริงผ่าน ข้อสังเกต: (1) `spark-ml` ต้องรันด้วย `-e PYTHONPATH=/workspace` ไม่งั้น import `sentiment` ไม่ได้ ต้องแก้ใน `infra/docker-compose.yml` เป็นงานแยก (2) CI ติดตั้งเฉพาะกลุ่ม `dev` จึงข้ามเทสต์ที่ใช้ fastapi (3) ข่าวจริงยังเป็นภาษาอังกฤษจนกว่าจะเลือกวิธีแปล
