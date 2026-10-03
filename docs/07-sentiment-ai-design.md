# 07 — Sentiment & AI Design

## FinBERT (O3)
- โมเดล pretrained FinBERT ไม่ฝึกใหม่ (นอกขอบเขต) — ใช้ใน Spark Structured Streaming ผ่าน wrapper ใน `sentiment/`
- Input: `headline` (+ `summary` ถ้ามี); Output: label, score, `model_name`, `model_version`
- เปลี่ยนโมเดล = เพิ่ม `model_version` ใหม่ แล้วรัน reprocess job จากชั้น Raw (FR-2.6)

### Gold set
- 300 ข่าวสุ่มแบบ stratified ตามหุ้นและเดือน
- M1 และ M2 ติดป้ายแยกกัน → วัด Cohen's kappa → ตกลงป้ายที่ไม่ตรงกัน
- เก็บที่ `sentiment/goldset/` (ไม่เก็บเนื้อข่าวเต็ม เก็บ `news_id`, headline, url, label)
- PoC: วัด F1 บน 100 ข่าว + throughput (ข่าว/วินาที)

## LLM Summary (O5)
- Input: ข่าวของหุ้นในวันนั้นจากชั้น Cleaned + ป้าย FinBERT เท่านั้น
- Output: 3–5 ประโยค สรุปข่าว + เหตุผลของ sentiment ภาพรวม
- Prompt ต้องห้ามแต่งข้อมูลนอกข่าวที่ให้ และห้ามแนะนำซื้อขาย
- Cache ต่อ `(ticker, trade_date, model_version)` เพื่อคุมค่าใช้จ่าย

## News RAG (O5)
- Index: embedding ของข่าวในชั้น Cleaned พร้อม metadata `ticker`, `published_at`, `source`, `url`
- Retrieval กรองด้วย ticker ที่ตรวจจากคำถามก่อนเสมอ
- Guardrail ก่อนเรียก LLM: ticker ไม่อยู่ใน `config/tickers.yaml` / ขอคำแนะนำซื้อขาย / นอกเรื่อง → ปฏิเสธ
- คำตอบต้องมี citation (headline, source, time) ทุกข้อความที่อ้างข้อเท็จจริง
- Baseline เปรียบเทียบ: LLM เดียวกันโดยไม่มี RAG

## ยังไม่ล็อก
ผู้ให้บริการ LLM / embedding และ vector store — ตัดสินใจใน ADR หลัง PoC (issue F6-01, F7-01)
