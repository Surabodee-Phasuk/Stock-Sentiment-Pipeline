# `streaming/`

Spark Structured Streaming: Kafka → `raw_news` → `clean_news` (MERGE ตัดซ้ำ) + FinBERT → `news_sentiment`

**Owner:** M1 (Raw/Cleaned), M2 (FinBERT)  
**Issues:** F2-02, F2-03, F3-01

## Kafka → `raw_news` (F2-02)
| ไฟล์ | หน้าที่ |
|---|---|
| `raw_news_stream.py` | อ่าน topic `stock-news` แล้ว append ลง `raw_news` ทุก 60 วินาที พร้อม checkpoint บน S3 |
| `check_raw_news.py` | นับข่าว แยกตามแหล่งและหุ้น และวัดเวลาของข่าวใหม่ แยกเป็นช่วง feed กับช่วง pipeline |

```bash
# อ่านทุกข้อความที่มีอยู่แล้วจบ (ทดสอบ)
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit streaming/raw_news_stream.py --once

# รันต่อเนื่อง (Ctrl+C เพื่อหยุด รันใหม่จะอ่านต่อจากจุดเดิม)
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit streaming/raw_news_stream.py

# เช็กผล
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit streaming/check_raw_news.py
```

### ข้อควรรู้
- Raw เก็บทุก event แม้ JSON ผิดรูป: ฟิลด์ข่าวเป็น null แต่ `raw_value` ยังอยู่ และ `ticker` ใช้ key ของ Kafka แทน การกรองอยู่ที่ F2-03
- ข่าวเดียวกันอาจอยู่ใน Raw หลายแถว (เช่น collector รีสตาร์ทแล้วส่งซ้ำ) ซึ่งเป็นเรื่องปกติของชั้นนี้ F2-03 เป็นตัวตัดซ้ำ
- checkpoint อยู่ที่ `s3a://stock-sentiment-lakehouse-surabodee/checkpoints/raw_news` ห้ามลบถ้าไม่ได้ตั้งใจอ่านใหม่ทั้งหมด เพราะจะอ่าน topic ตั้งแต่ต้นและเขียนซ้ำ
- Kafka เก็บข้อความ 7 วัน ถ้าหยุด stream นานกว่านั้น ข่าวส่วนเกินจะหาย

## `raw_news` → `clean_news` (F2-03)
`clean_news_job.py` อ่าน `raw_news` แบบ streaming แล้ว MERGE ลง `clean_news` หนึ่งแถวต่อ `(news_id, ticker)` ([ADR-0007](../docs/adr/0007-clean-news-key-news-id-ticker.md))

```bash
# ประมวลผลข่าวใน raw ที่ยังไม่เคยอ่านแล้วจบ (บรรทัดสุดท้ายบอก duplicate_rate)
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit streaming/clean_news_job.py --once

# รันต่อเนื่องทุก 60 วินาที คู่กับ raw_news_stream.py
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit streaming/clean_news_job.py
```

| ไม่รับแถวเมื่อ | เหตุผลที่แสดง |
|---|---|
| `news_id`, `ticker`, `headline` หรือ `url` ว่าง | `missing_field` |
| `published_at` ว่าง, ก่อนปี 2000 หรือเกินเวลาที่โหลดเข้า raw 1 ชั่วโมง | `bad_timestamp` |
| `ticker` ไม่อยู่ใน `config/tickers.yaml` | `unknown_ticker` |

- เก็บแถวแรกที่เจอของแต่ละคีย์ คือแหล่งแรกและ `ingested_at` แรก
- MERGE เพิ่มเฉพาะคีย์ที่ยังไม่มี รันซ้ำได้ ข่าวไม่ซ้ำ
- แถวที่ไม่ผ่านยังอยู่ใน `raw_news` ถ้าแก้กฎแล้วอยากประมวลผลใหม่ ให้ลบ checkpoint `checkpoints/clean_news` แล้วรันใหม่ ข่าวที่มีแล้วจะไม่ถูกเพิ่มซ้ำ
- เช็ก duplicate rate ใน Athena ด้วย [`lakehouse/queries/f2_03_duplicate_rate.sql`](../lakehouse/queries/f2_03_duplicate_rate.sql)

ดูกฎการทำงานที่ [docs/agents.md](../docs/agents.md)
