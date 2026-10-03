# Architecture Decision Log

## DEC-001 — Data Lakehouse เป็นแกนหลัก
เลือก Data Lakehouse (S3 + Apache Iceberg) เพราะเก็บข่าวดิบไว้ประมวลผลใหม่ได้เมื่อเปลี่ยนโมเดล, time travel ได้ และใช้ข้อมูลชุดเดียวกันหลายงานผ่าน SQL

## DEC-002 — ~50 หุ้นสหรัฐฯ
ขอบเขตหุ้นสหรัฐฯ ~50 ตัวหลายกลุ่มอุตสาหกรรม (PoC ใช้ 10 ตัว) ไม่รวมหุ้นไทยและคริปโต

## DEC-003 — Sentiment-first, ไม่ใช่การทำนายราคา
เว็บแอปเน้น Positive / Neutral / Negative ของข่าว เทียบกับราคาปิด ไม่ทำนายราคาหรือแนะนำซื้อขาย

## DEC-004 — Primary Owner + Secondary Owner
แต่ละคนดูแล subsystem แต่ต้องเข้าใจทั้ง pipeline

## DEC-005 — ข้อมูลเข้า 2 ทาง ตารางเดียว
ข่าว streaming (Kafka + Spark Structured Streaming) และราคาปิด batch (Yahoo Finance) ลงตาราง Iceberg ชุดเดียวกัน

## DEC-006 — ข่าวเท่านั้น ราคาปิดรายวัน
ไม่เก็บโพสต์โซเชียล (X, Reddit, StockTwits) และไม่เก็บราคาระหว่างวัน

## DEC-007 — AWS stack และ FinBERT
S3 + Iceberg, Glue + Athena, FinBERT; ตัดสินใจแทนชุดเดิม (MinIO, Nessie, Dremio/Trino, LSTM) ตาม proposal ล่าสุด Airflow ไม่อยู่ใน proposal: งาน batch ทำด้วย Spark batch

## DEC-008 — แผนสองเทอม
เทอม 1/2569 ทำ PoC; เทอม 2/2570 พัฒนาเต็ม ค่าเป้าหมายเป็นค่าเบื้องต้น ยืนยันหลัง PoC

## Open decisions
- แหล่งข่าว (RSS / News API) ที่ใช้จริงและ rate limit
- เทคโนโลยีเว็บแอป (frontend / API layer)
- ผู้ให้บริการ LLM / embedding และ vector store สำหรับ RAG
- Iceberg partition spec หลังทดสอบ
- วิธีรัน Spark / Kafka บน AWS (ควบคุมค่าใช้จ่าย ตั้ง budget alert)
