# 2-Person Work Plan

## Ownership model
ใช้ “Primary Owner + Secondary Owner” แต่ละคนดูแล subsystem หลักของตน แต่ต้องเข้าใจ pipeline ทั้งระบบพอที่จะ review, debug และนำเสนอได้

## Member 1 — สุรบดี ผาสุข
Primary: Data Platform / Ingestion / Lakehouse
- AWS (S3, Glue, Athena) และ budget alert
- Kafka และ news collector (RSS / News API), ดึงราคาปิด Yahoo Finance
- Iceberg บน S3 (Raw / Cleaned / Aggregated), partitioning, time travel, schema evolution
- ตัดข่าวซ้ำและ idempotency
- ความน่าเชื่อถือของ pipeline (checkpoint, ทำงานต่อเนื่อง 7 วัน)

Secondary: Spark streaming, FinBERT data contract, query ที่เว็บแอปต้องใช้

## Member 2 — รพินทร์ นะราช
Primary: Processing / Sentiment / Web App
- Spark Structured Streaming และ Spark batch
- FinBERT integration และประเมิน Macro-F1 (ติดป้าย 300 ข่าว)
- Aggregation รายหุ้นรายวัน
- เว็บแอป Search / Home / Stock Detail, UX/UI, SUS test

Secondary: Kafka, Iceberg layout, data quality

## Shared
- Architecture decisions, data schema review, integration testing
- LLM สรุปข่าว และ News RAG (เทอม 1 PoC, เทอม 2 พัฒนาเต็ม)
- Git/GitHub workflow, final presentation and demo
