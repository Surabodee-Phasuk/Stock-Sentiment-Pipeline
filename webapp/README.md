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
| `/stock/{ticker}` | Stock Detail | ข้อมูลตัวอย่าง |
| `/ask` | Ask AI | ต้นแบบ (ระบบจริง F7 เทอม 2) |
| `/api/docs` | เอกสาร API อัตโนมัติ | |

ข้อมูลตัวอย่าง `static/mock/stocks.json`: ข่าวคือข่าวจริงหนึ่งรอบของ collector (20 พ.ย. 2569) พร้อมป้าย FinBERT จริง ส่วนราคาและกราฟรายวันเป็นค่าสุ่ม ทุกหน้าที่ใช้ข้อมูลนี้มีป้าย "ข้อมูลตัวอย่าง"
