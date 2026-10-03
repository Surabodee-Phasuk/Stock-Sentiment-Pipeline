# ADR-0003: AWS Glue Data Catalog + Amazon Athena เป็น catalog และ query engine

**Status:** Accepted

## Decision
ลงทะเบียนตาราง Iceberg ใน Glue และ query ผ่าน Athena ทั้งงานวิเคราะห์และเว็บแอป (เว็บอ่านชั้น Aggregated)

## Consequences
- ไม่ต้องดูแล query engine เอง (แทน Dremio / Trino)
- คิดเงินตามข้อมูลที่สแกน → partition ต้อง benchmark (F2-07) และตั้ง budget alert
