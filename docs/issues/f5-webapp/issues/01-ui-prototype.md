# F5-01: Prototype ครบ 4 หน้า + ตัดสินใจเทคโนโลยีเว็บ (ADR)

**Status:** in-review  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-4.1–FR-4.4  
**Branch:** `feat/f5-01-ui-prototype`  
**PR:** [#35](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/35)

## งาน

- [x] prototype Search / Home / Stock Detail / Ask AI
- [x] ชุดสี sentiment
- [x] ADR เลือกเทคโนโลยี frontend / API

## Acceptance criteria

- Prototype ครบ 4 หน้า

## File scope

`webapp/`, `docs/adr/`

## Evidence

**Prototype ครบ 4 หน้า** รันด้วย `uvicorn webapp.api.main:app` (ADR-0008: FastAPI + HTML/JS ล้วน)

| หน้า | route | สิ่งที่แสดง | state ที่ทำแล้ว |
|---|---|---|---|
| Home (หุ้นที่ติดตาม) | `/` | รายการหุ้นที่เลือก: โลโก้, ticker, ชื่อ, ป้าย sentiment ส่วนใหญ่, ปุ่ม + เพิ่มหุ้น | watchlist ว่าง (ปุ่มไป Search), loading, error |
| Search (ค้นหาหุ้น) | `/search` | ค้นด้วย ticker / ชื่อ, chip กรองกลุ่มอุตสาหกรรม, ติ๊กเลือกหลายหุ้นแล้วกดบันทึกเข้ารายการติดตาม | ไม่พบผล |
| Stock Detail | `/stock/{ticker}` | ภาพรวมความรู้สึกของข่าว (ป้าย + วงกลมสัดส่วน), ราคาปิดล่าสุด, ข่าวล่าสุดพร้อมเวลา/แหล่ง/ป้าย/score, ช่องสรุป LLM (เทอม 2) | ticker นอกระบบ, ไม่มีข่าว, loading, error |
| Ask AI | `/ask` | หน้าเปล่าบอกว่าเป็นต้นแบบ ระบบถามตอบเปิดใช้ในเทอม 2 (F7) แบบหน้าจอถามตอบเก็บไว้ทำใน Figma | — |

- หน้าตาตามดีไซน์ของทีม (พื้นขาว สีหลักน้ำเงิน) ชุดสี sentiment อยู่ใน ADR-0008 และ `webapp/static/css/app.css` ใช้คู่กับคำ เชิงบวก / เป็นกลาง / เชิงลบ เสมอ
- หน้าเว็บเป็นภาษาไทยทั้งหมด หัวข้อข่าวตัวอย่าง 79 หัวข้อมีคำแปลไทย (แปลด้วย Claude) แสดงคู่กับต้นฉบับภาษาอังกฤษ ข่าวจริงในระบบยังไม่มีการแปล
- ทุกหน้าที่แสดง sentiment / คำตอบ AI มีข้อความ "ไม่ใช่คำแนะนำการลงทุน" (FR-4.5)
- ข้อมูลตัวอย่าง `static/mock/stocks.json`: ข่าวจริงหนึ่งรอบ (20 พ.ย. 2569) + ป้าย FinBERT จริง ราคาเป็นค่าสุ่ม มีป้าย "ข้อมูลตัวอย่าง" ที่กล่องราคาในหน้า Stock Detail และข้อความกำกับในหน้า Home
- `pytest webapp`: 8 passed (4 หน้า render, `/api/tickers`, disclaimer, mock ครบ 10 หุ้น, ทุกข่าวมีหัวข้อภาษาไทย)
- ภาพหน้าจอทั้ง 4 หน้าแนบใน PR

## Comments

- 2026-11-20 (M2): เพิ่ม `webapp/api/main.py`, หน้า `webapp/static/` 4 หน้า, ADR-0008 และ dependency group `web` ใน `pyproject.toml` (นอก File scope เพื่อให้ CI ติดตั้ง FastAPI) โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
- 2026-11-23 (M1): เปลี่ยนข้อความบนหน้าเว็บเป็นภาษาไทย เพิ่มคำแปลหัวข้อข่าวตัวอย่าง และป้ายกำกับราคาตัวอย่าง ส่วนกราฟ sentiment เทียบราคาปิดย้ายไปทำในเทอม 2 (F5-05) และช่องถามตอบในหน้า Ask AI ย้ายไปเทอม 2 (F7-02) เก็บเป็นแบบใน Figma ก่อน โค้ดและคำแปลเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
