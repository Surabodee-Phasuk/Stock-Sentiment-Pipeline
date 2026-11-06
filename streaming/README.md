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

ดูกฎการทำงานที่ [docs/agents.md](../docs/agents.md)
