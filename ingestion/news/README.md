# `ingestion/news/`

News collector (F1-01): ดึงข่าวของทุก ticker ใน [`config/tickers.yaml`](../../config/tickers.yaml) ทุก 5–15 นาที แล้วส่งเข้า Kafka topic `stock-news` (key = ticker) ตาม schema ใน [docs/05](../../docs/05-data-design.md)

| ไฟล์ | หน้าที่ |
|---|---|
| `event.py` | `NewsEvent`, normalize URL, `news_id` = sha256(URL ที่ normalize) |
| `sources.py` | แหล่งข่าว (PoC: Yahoo Finance RSS ต่อ ticker) + retry/backoff |
| `sinks.py` | ส่งเข้า Kafka หรือเขียน JSON Lines ออก stdout |
| `collector.py` | วนดึงทุก ticker ทุกรอบ, ไม่ส่งข่าวเดิมซ้ำในโปรเซสเดียวกัน, CLI |

## รัน
```bash
uv venv .venv && uv pip install --python .venv -r ingestion/news/requirements.txt pytest ruff

# ทดสอบโดยไม่ต้องมี Kafka: ดึงหนึ่งรอบแล้วพิมพ์ event ออกมา
.venv/bin/python -m ingestion.news.collector --once --sink stdout

# ใช้งานจริง: วนทุก 10 นาที ส่งเข้า Kafka (ต้องมี Kafka จาก INFRA-03)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 .venv/bin/python -m ingestion.news.collector --interval-min 10

.venv/bin/pytest ingestion/news
```

ตัวเลือก: `--interval-min` (5–15), `--delay` (วินาทีระหว่าง request, ค่าเริ่ม 1), `--topic`, `--tickers-file`, `--log-level`

## ข้อควรรู้
- การตัดซ้ำที่นี่เป็นแค่ cache ในหน่วยความจำ ถ้า restart จะส่งข่าวเดิมซ้ำได้ การตัดซ้ำจริงอยู่ที่ `clean_news` (F2-03)
- ข่าวชิ้นเดียวอาจอยู่ใน feed ของหลาย ticker จึงส่ง event แยกต่อ ticker โดยใช้ `news_id` เดียวกัน
- `url` เก็บ URL ต้นทางตามที่ feed ให้มา ส่วน `news_id` คิดจาก URL ที่ตัด tracking params แล้ว
