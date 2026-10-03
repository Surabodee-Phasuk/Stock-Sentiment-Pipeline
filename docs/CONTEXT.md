# CONTEXT — Glossary

นิยามเดียวต่อคำ ใช้คำเหล่านี้ให้ตรงกันในโค้ด เอกสาร commit และ UI

| คำ | ความหมาย |
|---|---|
| **ticker** | สัญลักษณ์หุ้นสหรัฐฯ ตัวพิมพ์ใหญ่ (เช่น `RKLB`) ต้องอยู่ใน `config/tickers.yaml` |
| **news / ข่าว** | บทความข่าวภาษาอังกฤษจาก RSS / News API (ไม่รวมโพสต์โซเชียล) |
| **daily close / ราคาปิด** | ราคาปิดรายวันจาก Yahoo Finance (ไม่มีราคาระหว่างวัน) |
| **sentiment** | label `positive` / `neutral` / `negative` จาก FinBERT ต่อข่าวหนึ่งชิ้น |
| **daily sentiment** | ภาพรวม sentiment ของหุ้นหนึ่งตัวในหนึ่งวันซื้อขาย (ตาราง `sentiment_daily`) |
| **Raw / Cleaned / Aggregated** | สามชั้นของ Lakehouse: ข้อมูลดิบ / ตัดซ้ำ + sentiment / สรุปรายหุ้นรายวัน |
| **reprocess** | รัน sentiment ใหม่จากชั้น Raw ด้วย `model_version` ใหม่ โดยไม่ดึงข่าวใหม่ |
| **time travel** | query ตาราง Iceberg ณ snapshot / เวลาก่อนหน้า |
| **near real-time** | ข่าวขึ้นเว็บภายใน 15 นาทีหลังเผยแพร่ (ไม่ใช้คำว่า real-time เฉยๆ) |
| **gold set** | ชุด 300 ข่าวที่ทีมติดป้ายเอง ใช้วัด FinBERT |
| **PoC** | Proof of Concept เทอม 1/2569 |
| **watchlist** | รายการหุ้นที่ผู้ใช้เลือก แสดงในหน้า Home |
| **Ask AI** | หน้า News RAG |
| **M1 / M2** | สุรบดี / รพินทร์ |
