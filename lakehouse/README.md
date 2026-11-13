# `lakehouse/`

DDL ตาราง Iceberg (`ddl/`), Athena queries (`queries/`), สาธิต time travel / schema evolution (`demo/`)

**Owner:** M1  
**Issues:** F2-01, F2-05, F2-07

## ตาราง (F2-01)
schema ทั้งหมดอยู่ใน [docs/05](../docs/05-data-design.md) ไฟล์ DDL เรียงตามชั้น Raw → Cleaned → Aggregated

| ไฟล์ | ตาราง | ชั้น | partition | คีย์ |
|---|---|---|---|---|
| `ddl/01_raw_news.sql` | `raw_news` | Raw | `days(published_at)` | — (append) |
| `ddl/02_raw_daily_price.sql` | `raw_daily_price` | Raw | `years(trade_date)` | — (append) |
| `ddl/03_clean_news.sql` | `clean_news` | Cleaned | `days(published_at)` | `news_id, ticker` ([ADR-0007](../docs/adr/0007-clean-news-key-news-id-ticker.md)) |
| `ddl/04_news_sentiment.sql` | `news_sentiment` | Cleaned | `days(published_at)` | `news_id, ticker, model_version` |
| `ddl/05_daily_price.sql` | `daily_price` | Cleaned | `years(trade_date)` | `ticker, trade_date` |
| `ddl/06_sentiment_daily.sql` | `sentiment_daily` | Aggregated | `years(trade_date)` | `ticker, trade_date, model_version` |

## สร้างตาราง
```bash
# ดู SQL ที่จะรัน (ไม่ต่อ AWS ไม่ต้องมี Spark)
.venv/bin/python -m lakehouse.ddl.create_tables --dry-run

# สร้างจริงใน Glue ผ่าน Spark ใน Docker (เปิด Docker และตั้งค่า AWS ก่อน)
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml exec spark \
  /opt/spark/bin/spark-submit lakehouse/ddl/create_tables.py
```
ต้องจบด้วย `all 6 tables ready in glue.stock_sentiment` จากนั้นเช็กใน Athena ด้วย [`queries/f2_01_check_tables.sql`](queries/f2_01_check_tables.sql)

## ข้อควรรู้
- รันซ้ำได้: ทุกไฟล์ใช้ `CREATE TABLE IF NOT EXISTS` ตารางที่มีอยู่แล้วจะไม่ถูกแก้หรือลบ (ขึ้นว่า `exists`)
- แก้ไฟล์ DDL แล้วรันใหม่ **ไม่**เปลี่ยนตารางที่มีอยู่ ถ้าจะเพิ่มคอลัมน์ให้ใช้ `ALTER TABLE ... ADD COLUMN` (schema evolution, F2-05) แล้วแก้ DDL กับ docs/05 ให้ตรงกัน
- Iceberg ไม่บังคับคีย์ (ไม่มี primary key) คีย์ในตารางข้างบนคือคีย์ที่งาน MERGE ใช้ เขียนไว้ใน `COMMENT` ของแต่ละตาราง
- partition spec ยังเป็นร่าง ล็อกหลัง benchmark (F2-07)
