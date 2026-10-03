# ADR-0002: ข่าวเข้าแบบ streaming (Kafka + Spark Structured Streaming), ราคาปิดเข้าแบบ batch

**Status:** Accepted

## Context
ข่าวต้องขึ้นเว็บภายใน 15 นาที แต่ราคามีเฉพาะราคาปิดรายวัน

## Decision
- ข่าว: collector → Kafka topic `stock-news` → Spark Structured Streaming (checkpoint) → Iceberg
- ราคาปิด: Spark batch วันละครั้ง → Iceberg (ไม่ผ่าน Kafka)
- ทั้งสองทางลงตาราง Iceberg ชุดเดียวกัน

## Consequences
- ต้องพิสูจน์ว่า batch + streaming อยู่ในตารางเดียวกันและ query ร่วมได้
- ไม่ใช้ Airflow: proposal ไม่ได้ระบุ; งาน batch ตั้งเวลาด้วย scheduler ที่ง่ายที่สุดที่ทำงานได้ (ตัดสินใจใน INFRA-02)
