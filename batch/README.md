# `batch/`

Spark batch: ราคาปิด (`price/`), aggregation รายวัน (`aggregation/`), reprocess sentiment จาก Raw (`reprocess/`)

**Owner:** M2  
**Issues:** F2-04, F3-04, F4-01

## ราคาปิด → `raw_daily_price` / `daily_price` (F2-04)
`price/load_daily_price.py` อ่านไฟล์จาก F1-02 (`data/price/daily_close_*.jsonl`) แล้ว
1. append ทุกแถวลง `raw_daily_price` (Raw เก็บทุกการโหลด)
2. ตัดแถวที่ไม่ผ่านการตรวจ แล้วเลือกแถวล่าสุดต่อ `(ticker, trade_date)`
3. MERGE เข้า `daily_price`: คีย์ใหม่ให้เพิ่ม คีย์เดิมอัปเดตเมื่อ `ingested_at` ใหม่กว่า

```bash
# 1) ดึงราคาปิดลงไฟล์ (ในเครื่อง)
.venv/bin/python -m ingestion.price.collector

# 2) โหลดเข้าตาราง (ใน container)
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit batch/price/load_daily_price.py
```

| ไม่รับแถวเมื่อ | เหตุผลที่แสดง |
|---|---|
| `ticker`, `trade_date` หรือ `ingested_at` ว่างหรือรูปแบบผิด | `missing_field` |
| `close` ว่าง, NaN หรือไม่เกิน 0 | `bad_close` |
| `trade_date` ก่อนปี 2000 หรือเป็นวันในอนาคต | `bad_trade_date` |
| `ticker` ไม่อยู่ใน `config/tickers.yaml` | `unknown_ticker` |

- รันซ้ำได้: `daily_price` ไม่มีแถวซ้ำ ส่วน `raw_daily_price` จะมีแถวเพิ่มทุกครั้งที่โหลด
- ข้อมูลเก่ากว่าที่มีในตารางจะไม่ทับข้อมูลใหม่
- query ข่าวคู่ราคาใน Athena: [`lakehouse/queries/f2_04_news_with_price.sql`](../lakehouse/queries/f2_04_news_with_price.sql)
- log อาจขึ้น `WARN ... FileNotFoundException ... daily_close_*.jsonl` เมื่อใช้ `*` ใน path เป็นแค่คำเตือนของ Spark ไม่ใช่ error

ดูกฎการทำงานที่ [docs/agents.md](../docs/agents.md)
