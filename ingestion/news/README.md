# `ingestion/news/`

News collector (F1-01): ดึงข่าวของทุก ticker ใน [`config/tickers.yaml`](../../config/tickers.yaml) ทุก 5–15 นาที แล้วส่งเข้า Kafka topic `stock-news` (key = ticker) ตาม schema ใน [docs/05](../../docs/05-data-design.md)

| ไฟล์ | หน้าที่ |
|---|---|
| `event.py` | `NewsEvent`, normalize URL, `news_id` = sha256(URL ที่ normalize) |
| `sources.py` | แหล่งข่าว RSS ต่อ ticker: Yahoo Finance (`yahoo`), Nasdaq (`nasdaq`) + retry/backoff |
| `sinks.py` | ส่งเข้า Kafka หรือเขียน JSON Lines ออก stdout |
| `collector.py` | วนดึงทุก ticker ทุกรอบ, ไม่ส่งข่าวเดิมซ้ำในโปรเซสเดียวกัน, CLI |

## รัน
```bash
uv venv .venv && uv pip install --python .venv -r ingestion/news/requirements.txt pytest ruff

# ทดสอบโดยไม่ต้องมี Kafka: ดึงหนึ่งรอบแล้วพิมพ์ event ออกมา
.venv/bin/python -m ingestion.news.collector --once --sink stdout

# ใช้งานจริง: วนทุก 10 นาที ส่งเข้า Kafka (เปิด Kafka ก่อนตาม infra/README.md)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 .venv/bin/python -m ingestion.news.collector --interval-min 10

.venv/bin/pytest ingestion/news
```

ตัวเลือก: `--sources` (ค่าเริ่ม `yahoo,nasdaq`), `--interval-min` (5–15), `--delay` (วินาทีระหว่าง request, ค่าเริ่ม 1), `--topic`, `--tickers-file`, `--log-level`

## ข้อควรรู้
- การตัดซ้ำที่นี่เป็นแค่ cache ในหน่วยความจำ ถ้า restart จะส่งข่าวเดิมซ้ำได้ การตัดซ้ำจริงอยู่ที่ `clean_news` (F2-03)
- ข่าวชิ้นเดียวอาจอยู่ใน feed ของหลาย ticker จึงส่ง event แยกต่อ ticker โดยใช้ `news_id` เดียวกัน
- `url` เก็บ URL ต้นทางตามที่ feed ให้มา ส่วน `news_id` คิดจาก URL ที่ตัด tracking params แล้ว
- (F1-03) แต่ละแหล่งถูกดึงแยกกัน แหล่งหนึ่งล้ม (`failed=rss:nasdaq:AAPL`) อีกแหล่งยังส่งต่อ ช่วยลดผลจาก rate limit (FR-1.5)
- (F1-03) ข่าวเดียวกันจากหลายแหล่งได้ `news_id` เดียวกันเมื่อ URL หลัง normalize ตรงกัน แต่ Yahoo ลิงก์ไปเว็บต้นทาง (fool.com ฯลฯ) ส่วน Nasdaq ลิงก์ไป `nasdaq.com/articles/...` จึงซ้ำกันจริงไม่บ่อย (รัน 2026-10-25: 311 event, ซ้ำข้ามแหล่ง 0)
- Nasdaq ไม่มีข่าว RKLB และมีน้อยสำหรับ SPCX ส่วน Yahoo ครอบคลุมทั้งคู่
- ไม่ใช้ Seeking Alpha (ทุก item ลิงก์ไปหน้า symbol เดียวกัน `news_id` จะชนกัน) และ Google News (ลิงก์เป็น redirect)
