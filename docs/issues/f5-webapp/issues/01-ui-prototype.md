# F5-01: Prototype ครบ 4 หน้า + ตัดสินใจเทคโนโลยีเว็บ (ADR)

**Status:** in-review  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-4.1–FR-4.4  
**Branch:** `feat/f5-01-ui-prototype`  
**PR:** —

## งาน

- [x] prototype Search / Home / Stock Detail / Ask AI
- [x] ชุดสี sentiment
- [x] ADR เลือกเทคโนโลยี frontend / API

## Acceptance criteria

- Prototype ครบ 4 หน้า

## File scope

`webapp/`, `docs/adr/`

## Evidence

**Prototype ครบ 4 หน้า** รันด้วย `uvicorn webapp.api.main:app` (ADR-0008: FastAPI + HTML/JS ล้วน + Chart.js)

| หน้า | route | สิ่งที่แสดง | state ที่ทำแล้ว |
|---|---|---|---|
| Home (My Watchlist) | `/` | รายการหุ้นที่เลือก: โลโก้, ticker, ชื่อ, ป้าย sentiment ส่วนใหญ่, ปุ่ม + Add More | watchlist ว่าง (ปุ่มไป Search), loading, error |
| Search (Stock Selection) | `/search` | ค้นด้วย ticker / ชื่อ, chip กรองกลุ่มอุตสาหกรรม, ติ๊กเลือกหลายหุ้นแล้วกด Add to Watchlist | ไม่พบผล |
| Stock Detail | `/stock/{ticker}` | Overall Sentiment (ป้าย + วงกลมสัดส่วน), Latest Price, Latest News พร้อมเวลา/แหล่ง/ป้าย/score, กราฟ sentiment รายวันเทียบราคาปิด 30 วันทำการ, ช่องสรุป LLM (เทอม 2) | ticker นอกระบบ, ไม่มีข่าว, loading, error |
| Ask AI | `/ask` | ช่องถาม + คำตอบพร้อม citation (จำลองจากข่าวตัวอย่าง) | ปฏิเสธคำถามซื้อขาย, ปฏิเสธนอกขอบเขต |

- หน้าตาตามดีไซน์ของทีม (พื้นขาว สีหลักน้ำเงิน) ชุดสี sentiment อยู่ใน ADR-0008 และ `webapp/static/css/app.css` ใช้คู่กับคำ Positive / Neutral / Negative เสมอ
- ทุกหน้าที่แสดง sentiment / คำตอบ AI มีข้อความ "ไม่ใช่คำแนะนำการลงทุน" (FR-4.5)
- ข้อมูลตัวอย่าง `static/mock/stocks.json`: ข่าวจริงหนึ่งรอบ (20 พ.ย. 2569) + ป้าย FinBERT จริง ราคาเป็นค่าสุ่ม ระบุว่าเป็นข้อมูลตัวอย่างในหน้า
- `pytest webapp`: 7 passed (4 หน้า render, `/api/tickers`, disclaimer, mock ครบ 10 หุ้น)
- ภาพหน้าจอทั้ง 4 หน้าแนบใน PR

## Comments

- 2026-11-20 (M2): เพิ่ม `webapp/api/main.py`, หน้า `webapp/static/` 4 หน้า, ADR-0008 และ dependency group `web` ใน `pyproject.toml` (นอก File scope เพื่อให้ CI ติดตั้ง FastAPI) โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
