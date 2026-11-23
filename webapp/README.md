# `webapp/`

เว็บแอป (Search, Home, Stock Detail, Ask AI) และ API layer (`api/`) — เทคโนโลยีตาม [ADR-0008](../docs/adr/0008-web-fastapi-static-frontend.md)

**Owner:** M2  
**Issues:** F4-02, F5-*

ดูกฎการทำงานที่ [docs/agents.md](../docs/agents.md)

## รันในเครื่อง
```bash
.venv/bin/python -m pip install --group web
.venv/bin/uvicorn webapp.api.main:app --reload      # http://127.0.0.1:8000
```

| route | หน้า | ข้อมูล |
|---|---|---|
| `/` | Home (Watchlist) | ข้อมูลตัวอย่าง, watchlist เก็บใน browser |
| `/search` | Search | `/api/tickers` จาก `config/tickers.yaml` |
| `/stock/{ticker}` | Stock Detail | ข้อมูลจริงจาก Athena (F5-02), เติม `?mock=1` เพื่อดูข้อมูลตัวอย่าง |
| `/ask` | Ask AI | ต้นแบบ (ระบบจริง F7 เทอม 2) |
| `/api/stock/{ticker}?days=30` | JSON ของหน้า Stock Detail | 3 query Athena รันพร้อมกัน, cache 5 นาที |
| `/api/docs` | เอกสาร API อัตโนมัติ | |

ข้อมูลตัวอย่าง `static/mock/stocks.json`: ข่าวคือข่าวจริงหนึ่งรอบของ collector (20 พ.ย. 2569) พร้อมป้าย FinBERT จริง ส่วนราคาและกราฟรายวันเป็นค่าสุ่ม ทุกหน้าที่ใช้ข้อมูลนี้มีป้าย "ข้อมูลตัวอย่าง"

## ข้อมูลจริงจาก Athena (F5-02)
ต้องมี `aws configure` (credential เดียวกับ AWS CLI) และมีข้อมูลใน `news_sentiment` (F3-01), `clean_news` (F2-03), `daily_price` (F2-04)

| env | ค่าเริ่มต้น |
|---|---|
| `ATHENA_WORKGROUP` | `stock-sentiment` |
| `ATHENA_DATABASE` | `stock_sentiment` |
| `AWS_REGION` | `ap-southeast-2` |
| `MODEL_VERSION` | `finbert-v1` |

- กราฟรายวันใช้วันซื้อขายของ `daily_price` แล้วจับคู่กับข่าวที่เผยแพร่ในวันเดียวกันตามเวลานิวยอร์ก ข่าววันเสาร์–อาทิตย์จึงไม่อยู่ในกราฟ (แต่อยู่ในรายการข่าวล่าสุด)
- "ข่าว 24 ชม. ล่าสุด" นับจาก `published_at`
- Athena error (สิทธิ์, query ผิด, timeout 30 s) → API ตอบ 503 หน้าเว็บแสดงปุ่มลองใหม่
