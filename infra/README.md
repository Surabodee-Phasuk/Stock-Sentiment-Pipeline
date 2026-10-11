# `infra/`

Docker Compose (Kafka, Spark สำหรับพัฒนาในเครื่อง) และสคริปต์/คู่มือ setup AWS (S3, Glue, Athena, IAM, budget alert)

**Owner:** M1  
**Issues:** INFRA-02, INFRA-03

ดูกฎการทำงานที่ [docs/agents.md](../docs/agents.md)

| ไฟล์ | หน้าที่ |
|---|---|
| `docker-compose.yml` | Kafka (KRaft โหนดเดียว), สร้าง topic `stock-news`, Spark (local mode) |
| `.env.example` | ค่าที่ปรับได้ คัดลอกเป็น `infra/.env` |
| `spark/spark-defaults.conf` | jar ของ Iceberg / Kafka connector และ Glue catalog ชื่อ `glue` |
| `spark/smoke_iceberg.py` | ทดสอบ Spark เขียน/อ่าน Iceberg บน S3 ผ่าน Glue |
| `spark/smoke_kafka.py` | ทดสอบ Spark อ่าน topic `stock-news` |

## Local Kafka + Spark (INFRA-03)

เวอร์ชัน: Kafka 4.3.1, Spark 4.0.4 (Scala 2.13, Java 17, Python 3), Iceberg 1.12.0

ต้องมี Docker Desktop และ `aws configure` ไว้แล้ว (ดู INFRA-02) รันทุกคำสั่งจาก root ของ repo

```bash
cp infra/.env.example infra/.env                 # ครั้งแรก (ไม่ทำก็ได้ ถ้าใช้ profile default)
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps    # kafka = healthy, kafka-init = exited (0), spark = running
docker compose -f infra/docker-compose.yml logs kafka-init   # ต้องเห็น Topic: stock-news PartitionCount: 3
```

| จาก | Kafka bootstrap |
|---|---|
| เครื่องเรา (collector, test) | `localhost:9092` |
| container อื่น (Spark) | `kafka:19092` |

### 1. Produce / consume ข้อความทดสอบ (acceptance criteria)
```bash
# ส่งข้อความ key:value หนึ่งบรรทัด
echo 'AAPL:{"hello":"kafka"}' | docker compose -f infra/docker-compose.yml exec -T kafka \
  /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka:19092 --topic stock-news \
  --property parse.key=true --property key.separator=:

# อ่านกลับ
docker compose -f infra/docker-compose.yml exec kafka \
  /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:19092 --topic stock-news \
  --from-beginning --property print.key=true --max-messages 1
```

### 2. News collector → Kafka (F1-01)
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 .venv/bin/python -m ingestion.news.collector --once
```

### 3. Spark อ่าน Kafka
```bash
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit infra/spark/smoke_kafka.py
```
ครั้งแรกจะโหลด jar สักพัก (เก็บ cache ไว้ใน volume `ivy-cache`)

### 4. Spark เขียน Iceberg บน S3 ผ่าน Glue
```bash
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/spark-submit infra/spark/smoke_iceberg.py
```
ต้องจบด้วย `iceberg smoke test passed` สคริปต์สร้างตาราง `stock_sentiment.zz_infra03_smoke` แล้วลบทิ้งเอง ใส่ `--keep` ถ้าอยากลอง query ผ่าน Athena ก่อน

### เปิด shell
```bash
docker compose -f infra/docker-compose.yml exec spark /opt/spark/bin/pyspark      # หรือ spark-sql
```
Spark UI: http://localhost:4040 (เฉพาะตอนมี job รันอยู่)

### ปิด
```bash
docker compose -f infra/docker-compose.yml stop     # หยุด เก็บข้อความใน Kafka ไว้
docker compose -f infra/docker-compose.yml down     # ลบ container → ข้อความใน Kafka หายหมด
```

### ข้อควรรู้
- Kafka ไม่ได้ mount volume ไว้: `down` แล้วข้อความกับ offset หายหมด ถ้า streaming job (F2-02) มี checkpoint ค้างอยู่ ให้ลบ checkpoint ด้วย ไม่อย่างนั้น offset จะไม่ตรงกัน
- container `spark` รันเป็น root เพื่ออ่าน `~/.aws` (mount แบบ read-only) ใช้สำหรับเครื่อง dev เท่านั้น
- ห้ามใส่ access key ใน `.env` หรือไฟล์ใดๆ ใน repo
- bucket ใน `spark-defaults.conf` ต้องตรงกับ INFRA-02 (`stock-sentiment-lakehouse-surabodee`)
