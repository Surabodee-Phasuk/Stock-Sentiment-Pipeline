# ADR-0001: Data Lakehouse บน Amazon S3 + Apache Iceberg

**Status:** Accepted

## Context
ข่าวสะสมทุกวันและต้องใช้ร่วมกันทั้งเว็บ การวิเคราะห์ และ LLM ต้องเก็บข่าวดิบไว้ประมวลผลใหม่เมื่อเปลี่ยนโมเดล และย้อนดูข้อมูล ณ เวลาก่อนหน้าได้

## Decision
ใช้ Amazon S3 เป็น storage และ Apache Iceberg เป็น table format แบ่งชั้น Raw / Cleaned / Aggregated

## Consequences
- ได้ time travel, schema evolution, MERGE (ตัดซ้ำ) และ reprocess จาก Raw
- ข่าวมีปริมาณไม่มาก (~500/วัน) จึงพิสูจน์คุณค่าด้วยความสามารถ ไม่ใช่ปริมาณ
- แทนชุดเดิม (MinIO + Nessie) ที่ไม่ได้อยู่ใน proposal ล่าสุด
