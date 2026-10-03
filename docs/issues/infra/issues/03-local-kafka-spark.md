# INFRA-03: Docker Compose: Kafka + Spark สำหรับพัฒนาในเครื่อง

**Status:** todo  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-1.1, FR-2.2  
**Branch:** `chore/infra-03-local-kafka-spark`  
**PR:** —

## งาน

- [ ] `infra/docker-compose.yml` มี Kafka และ Spark
- [ ] สร้าง topic `stock-news` อัตโนมัติ
- [ ] Spark เขียน Iceberg บน S3 ผ่าน Glue catalog ได้จากเครื่อง
- [ ] `.env.example`

## Acceptance criteria

- `docker compose up` แล้ว produce/consume ข้อความทดสอบได้

## File scope

`infra/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
