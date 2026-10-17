# INFRA-03: Docker Compose: Kafka + Spark สำหรับพัฒนาในเครื่อง

**Status:** in-review  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.1, FR-2.2  
**Branch:** `chore/infra-03-local-kafka-spark`  
**PR:** —

## งาน

- [x] `infra/docker-compose.yml` มี Kafka และ Spark
- [x] สร้าง topic `stock-news` อัตโนมัติ
- [x] Spark เขียน Iceberg บน S3 ผ่าน Glue catalog ได้จากเครื่อง
- [x] `.env.example`

## Acceptance criteria

- `docker compose up` แล้ว produce/consume ข้อความทดสอบได้

## File scope

`infra/`

## Evidence

ทดสอบเมื่อ 2026-10-17 บน macOS, Docker 29.4.3 (Docker Desktop: 8 CPU, RAM 4 GB)

**1. `docker compose up -d` → `ps`**
```
stock-sentiment-kafka-1        apache/kafka:4.3.1   Up 8 minutes (healthy)     0.0.0.0:9092->9092/tcp
stock-sentiment-kafka-init-1   apache/kafka:4.3.1   Exited (0)
stock-sentiment-spark-1        apache/spark:4.0.4-scala2.13-java17-python3-ubuntu   Up 8 minutes   0.0.0.0:4040->4040/tcp
```
`kafka-init` log: `Created topic stock-news.` · `PartitionCount: 3 ReplicationFactor: 1`

**2. Produce / consume (acceptance criteria)**
```
$ echo 'AAPL:{"hello":"kafka"}' | ... kafka-console-producer.sh ... --topic stock-news
$ ... kafka-console-consumer.sh ... --topic stock-news --from-beginning --max-messages 1
AAPL    {"hello":"kafka"}
Processed a total of 1 messages
```

**3. `smoke_kafka.py` — Spark อ่าน Kafka**
```
topic=stock-news messages=2
|ticker|count|
|  AAPL|    2|
kafka smoke test passed
```

**4. `smoke_iceberg.py` — Spark เขียน Iceberg บน S3 ผ่าน Glue**
```
rows=[(1, 'hello from local spark')]
location=s3://stock-sentiment-lakehouse-surabodee/warehouse/zz_infra03_smoke
snapshots=1
dropped glue.stock_sentiment.zz_infra03_smoke
iceberg smoke test passed
```

## Comments

- **2026-10-11 (M1):** เขียน config ครบแล้ว ยังไม่ได้รันทดสอบ
  - `infra/docker-compose.yml`: Kafka 4.3.1 (KRaft โหนดเดียว, ปิด auto-create topic), `kafka-init` สร้าง `stock-news` 3 partitions, Spark 4.0.4 local mode (mount `~/.aws` แบบ read-only)
  - `infra/spark/spark-defaults.conf`: Iceberg 1.12.0 + Kafka connector, Glue catalog ชื่อ `glue`
  - `infra/spark/smoke_kafka.py`, `infra/spark/smoke_iceberg.py`: สคริปต์ทดสอบ Spark ↔ Kafka และ Spark → Iceberg บน S3
  - `infra/.env.example` และวิธีใช้ใน `infra/README.md`
  - ค้าง: รัน `docker compose up` + produce/consume (acceptance criteria), รัน smoke test ทั้งสอง, แล้วเติม Evidence
- **2026-10-17 (Claude, ขอโดย M1):** sync `main` แล้ว (รวม INFRA-02 จาก PR #22) ยังไม่ได้รันทดสอบ — Docker daemon ในเครื่องยังไม่เปิด ค้างเหมือนเดิม: `docker compose up` + produce/consume, `smoke_kafka.py`, `smoke_iceberg.py` แล้วเติม Evidence
- **2026-10-17 (Claude, ขอโดย M1):** รันทดสอบครบ ผ่านทุกขั้น (ดู Evidence) และเปลี่ยนคำสั่ง console producer/consumer ใน `infra/README.md` เป็น `--reader-property` / `--formatter-property` เพราะ `--property` ถูก deprecate ใน Kafka 4.x
