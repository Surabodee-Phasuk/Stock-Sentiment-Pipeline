# `ingestion/price/`

Daily close collector (F1-02): ดึงราคาปิดรายวันของทุก ticker ใน [`config/tickers.yaml`](../../config/tickers.yaml) วันละครั้ง แล้วเขียน JSON Lines ตาม schema "Daily close (batch)" ใน [docs/05](../../docs/05-data-design.md) ให้ Spark batch (F2-04) อ่านต่อ ราคาปิดไม่ผ่าน Kafka

| ไฟล์ | หน้าที่ |
|---|---|
| `sources.py` | `DailyClose`, แปลงผล Yahoo Finance chart API เป็นราคาปิดรายวัน + retry/backoff |
| `collector.py` | วนดึงทุก ticker เว้นจังหวะระหว่างหุ้น, เขียนไฟล์หรือพิมพ์ออกจอ, CLI |

## รัน
```bash
# ทดสอบ: ดึงหนึ่งรอบแล้วพิมพ์ JSON Lines ออกจอ
.venv/bin/python -m ingestion.price.collector --sink stdout

# ใช้งานจริง (วันละครั้ง หลังตลาดสหรัฐฯ ปิด = หลัง 03:00 น. เวลาไทย ช่วง EDT / 04:00 น. ช่วง EST)
.venv/bin/python -m ingestion.price.collector
# → data/price/daily_close_<วันที่ UTC>.jsonl

.venv/bin/pytest ingestion/price
```

ตัวเลือก: `--days` (1–30 วันปฏิทินย้อนหลัง, ค่าเริ่ม 7), `--delay` (วินาทีระหว่างหุ้น, ค่าเริ่ม 2), `--out-dir`, `--tickers-file`, `--log-level`

ตัวอย่างหนึ่งแถว:
```json
{"ticker":"RKLB","trade_date":"2026-10-19","close":51.36,"source":"yahoo_finance","ingested_at":"2026-10-20T06:18:47Z"}
```

Spark ใน container อ่านได้จาก `/workspace/data/price/` เช่น `spark.read.json("/workspace/data/price/")`

## ข้อควรรู้
- เรียก endpoint `query1.finance.yahoo.com/v8/finance/chart` ตรงด้วย urllib (endpoint เดียวกับที่ yfinance ใช้) จึงไม่ต้องลง yfinance/pandas และไม่ต้องใช้ API key
- `trade_date` คือวันตามเวลาตลาดนิวยอร์ก ไม่ใช่วันตาม UTC และจะไม่เอาแท่งของวันที่ตลาดยังเปิดอยู่ เพราะยังไม่ใช่ราคาปิด
- ดึงย้อนหลัง 7 วันทุกครั้ง ถ้าวันไหนลืมรัน รอบถัดไปจะได้ราคาวันนั้นมาด้วย แถวซ้ำข้ามไฟล์ไม่เป็นปัญหาเพราะ `daily_price` MERGE on `ticker, trade_date` (F2-04)
- รันซ้ำในวันเดียวกันจะเขียนทับไฟล์ของวันนั้น ไม่ได้ไฟล์เพิ่ม
- `close` คือราคาปิดที่ปรับ split แล้วแต่ยังไม่ปรับปันผล (ค่า `close` ของ Yahoo) ปัดเป็นทศนิยม 4 ตำแหน่ง
- `data/` ถูก gitignore ไฟล์ราคาไม่ขึ้น repo
- ย้อนหลังตั้งแต่ปี 2020 สำหรับ ~50 หุ้นเป็นงาน backfill (F1-04)
