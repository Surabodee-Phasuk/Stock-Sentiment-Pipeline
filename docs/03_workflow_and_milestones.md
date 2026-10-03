# Development Workflow and Milestones

## Repository workflow
BACKLOG → TODO → IN PROGRESS → REVIEW → TESTING → DONE

ทุก task ระบุ Owner, Milestone, Dependencies, Acceptance criteria, Test evidence

## เทอม 1/2569 — Proof of Concept
พิสูจน์ว่าเครื่องมือแต่ละตัวใช้งานได้จริง

| งาน | สิ่งที่ต้องพิสูจน์ | เกณฑ์ผ่าน |
|---|---|---|
| ดึงข่าวสดและราคา | API ข่าวและ Yahoo Finance เชื่อมต่อได้ และรู้ rate limit จริง | ดึงข่าวและราคาของ 10 หุ้นได้ครบ |
| Kafka → Spark → Iceberg | ข่าวไหลจาก Kafka ลงตาราง Iceberg บน S3 ได้ | ข่าวใหม่ปรากฏในตารางภายใน 15 นาที |
| ราคาปิดแบบ batch | ราคาปิดรายวันกับข่าว streaming อยู่ในตารางชุดเดียวกัน | Query ข่าวคู่กับราคาผ่าน Athena ได้ |
| Time travel และ reprocess | ย้อนดูตาราง ณ เวลาก่อนหน้า และรัน sentiment ใหม่จากชั้น Raw ได้ | สาธิตได้กับข่าวชุดทดสอบ |
| FinBERT | ความแม่นและความเร็วบนข่าวจริง | วัด F1 บน 100 ข่าว และวัดจำนวนข่าวต่อวินาที |
| LLM สรุปข่าว | สรุปข่าวของหุ้นหนึ่งตัวได้ถูกต้อง | สรุป 5 ชิ้น ตรวจด้วยคน พร้อมค่าใช้จ่ายต่อชิ้น |
| News RAG | ค้นข่าวถูกหุ้นและตอบพร้อมแหล่งอ้างอิง | ตอบ 10 คำถามทดสอบได้ |
| UX/UI | ผู้ใช้เข้าใจหน้าจอ | Prototype ครบ 4 หน้า และหน้า Stock Detail ดึงข้อมูลจริงได้ |

## เทอม 2/2570 — พัฒนาเต็ม
ขยายเป็น ~50 หุ้น ข่าวย้อนหลังตั้งแต่ปี 2020 และพัฒนาตามวัตถุประสงค์ 5 ข้อให้ผ่านตัวชี้วัดใน 00_project_plan.md

## Milestones
- **M0 Planning Ready** — ขอบเขต สถาปัตยกรรม data contract และผู้รับผิดชอบตกลงแล้ว
- **M1 PoC Ingestion** — ดึงข่าวและราคา 10 หุ้นได้, Kafka รับข่าว
- **M2 PoC Lakehouse** — Kafka → Spark → Iceberg บน S3, batch ราคาปิด, Athena query, time travel และ reprocess
- **M3 PoC Models** — FinBERT F1 บน 100 ข่าว, LLM สรุป 5 ชิ้น, RAG 10 คำถาม
- **M4 PoC UI** — Prototype 4 หน้า, Stock Detail ดึงข้อมูลจริง
- **M5 Full Build (เทอม 2)** — ผ่านตัวชี้วัดทั้ง 5 วัตถุประสงค์: ทำงานต่อเนื่อง 7 วัน, Macro-F1 ≥ 0.70, SUS ≥ 68, LLM/RAG ≥ 90%
