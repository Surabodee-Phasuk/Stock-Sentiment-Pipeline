# ADR-0007: คีย์ของ `clean_news` คือ `(news_id, ticker)`

**Status:** Accepted (2026-10-27)

## Context
ข่าวชิ้นเดียวมักอยู่ใน feed ของหลายหุ้น ตอนทดสอบ F1-01 พบ 27 จาก 125 ข่าว (ประมาณ 20%) collector จึงส่ง event แยกต่อหุ้นโดยใช้ `news_id` เดียวกัน

ถ้า MERGE `clean_news` ด้วย `news_id` อย่างเดียว จะเหลือแถวเดียวต่อข่าวและติดไปกับหุ้นตัวเดียว ข่าวนั้นจะหายไปจากหน้า Stock Detail และ `sentiment_daily` ของหุ้นตัวอื่นที่เกี่ยวข้อง

## Decision
- `clean_news` มีหนึ่งแถวต่อ `(news_id, ticker)` และ MERGE ด้วยคีย์นี้ (F2-03)
- `news_sentiment` ใช้คีย์ `(news_id, ticker, model_version)` เพื่อให้ join กับ `clean_news` ได้ตรง และเก็บผลหลายเวอร์ชันโมเดลไว้เทียบกันได้ (F3-04)
- duplicate rate ในชั้น Cleaned (NFR-4) นับซ้ำตาม `(news_id, ticker)`

## Consequences
- ข่าวที่เกี่ยวกับหลายหุ้นถูกนับใน sentiment ของทุกหุ้นที่เกี่ยวข้อง ซึ่งตรงกับสิ่งที่ผู้ใช้เห็นใน feed ของแต่ละหุ้น
- FinBERT ประเมินข่าวชิ้นเดียวซ้ำตามจำนวนหุ้น (ข้อความเดียวกัน ผลเหมือนกัน) ถ้าเป็นภาระตอนขยายเป็น ~50 หุ้น ค่อย cache ผลตาม `news_id` (F3-01)
- ถ้าต้องการนับข่าวไม่ซ้ำทั้งระบบ ใช้ `count(DISTINCT news_id)`
