# INFRA-03: Docker Compose: Kafka + Spark สำหรับพัฒนาในเครื่อง

**Status:** in-progress  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.1, FR-2.2  
**Branch:** `chore/infra-03-local-kafka-spark`  
**PR:** —

## งาน

- [x] `infra/docker-compose.yml` มี Kafka และ Spark
- [x] สร้าง topic `stock-news` อัตโนมัติ
- [ ] Spark เขียน Iceberg บน S3 ผ่าน Glue catalog ได้จากเครื่อง
- [x] `.env.example`

## Acceptance criteria

- `docker compose up` แล้ว produce/consume ข้อความทดสอบได้

## File scope

`infra/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments

- **2026-10-11 (M1):** เขียน config ครบแล้ว ยังไม่ได้รันทดสอบ
  - `infra/docker-compose.yml`: Kafka 4.3.1 (KRaft โหนดเดียว, ปิด auto-create topic), `kafka-init` สร้าง `stock-news` 3 partitions, Spark 4.0.4 local mode (mount `~/.aws` แบบ read-only)
  - `infra/spark/spark-defaults.conf`: Iceberg 1.12.0 + Kafka connector, Glue catalog ชื่อ `glue`
  - `infra/spark/smoke_kafka.py`, `infra/spark/smoke_iceberg.py`: สคริปต์ทดสอบ Spark ↔ Kafka และ Spark → Iceberg บน S3
  - `infra/.env.example` และวิธีใช้ใน `infra/README.md`
  - ค้าง: รัน `docker compose up` + produce/consume (acceptance criteria), รัน smoke test ทั้งสอง, แล้วเติม Evidence
