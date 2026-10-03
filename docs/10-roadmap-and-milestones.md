# 10 — Roadmap & Milestones

รายการงานจริงอยู่ที่ [issues/BOARD.md](issues/BOARD.md) — หน้านี้คือภาพรวม

## เทอม 1/2569 — Proof of Concept
| งาน | สิ่งที่ต้องพิสูจน์ | เกณฑ์ผ่าน | Issue |
|---|---|---|---|
| ดึงข่าวสดและราคา | API ข่าวและ Yahoo Finance เชื่อมต่อได้ และรู้ rate limit จริง | ดึงข่าวและราคาของ 10 หุ้นได้ครบ | F1-01, F1-02 |
| Kafka → Spark → Iceberg | ข่าวไหลจาก Kafka ลงตาราง Iceberg บน S3 ได้ | ข่าวใหม่ปรากฏในตารางภายใน 15 นาที | F2-02 |
| ราคาปิดแบบ batch | ราคาปิดรายวันกับข่าว streaming อยู่ในตารางชุดเดียวกัน | Query ข่าวคู่กับราคาผ่าน Athena ได้ | F2-04 |
| Time travel และ reprocess | ย้อนดูตาราง ณ เวลาก่อนหน้า และรัน sentiment ใหม่จากชั้น Raw ได้ | สาธิตได้กับข่าวชุดทดสอบ | F2-05, F3-04 |
| FinBERT | ความแม่นและความเร็วบนข่าวจริง | วัด F1 บน 100 ข่าว และวัดจำนวนข่าวต่อวินาที | F3-01, F3-02 |
| LLM สรุปข่าว | สรุปข่าวของหุ้นหนึ่งตัวได้ถูกต้อง | สรุป 5 ชิ้น ตรวจด้วยคน พร้อมค่าใช้จ่ายต่อชิ้น | F6-01 |
| News RAG | ค้นข่าวถูกหุ้นและตอบพร้อมแหล่งอ้างอิง | ตอบ 10 คำถามทดสอบได้ | F7-01 |
| UX/UI | ผู้ใช้เข้าใจหน้าจอ | Prototype ครบ 4 หน้า และหน้า Stock Detail ดึงข้อมูลจริงได้ | F5-01, F5-02 |

## Milestones
| Milestone | เนื้อหา | Issues |
|---|---|---|
| M0 Planning Ready | ขอบเขต สถาปัตยกรรม data contract โครงสร้าง repo และ branch ตกลงแล้ว | INFRA-01 |
| M1 Infra Ready | AWS (S3/Glue/Athena/budget), Kafka + Spark local, CI | INFRA-02..04 |
| M2 PoC Ingestion | ข่าว + ราคา 10 หุ้น | F1-01..03 |
| M3 PoC Lakehouse | Kafka → Spark → Iceberg, batch ราคา, Athena, time travel | F2-01..05 |
| M4 PoC Models | FinBERT F1/throughput, reprocess, LLM 5 ชิ้น, RAG 10 คำถาม | F3-01, F3-02, F3-04, F6-01, F7-01 |
| M5 PoC UI | Prototype 4 หน้า, Stock Detail ข้อมูลจริง | F5-01, F5-02 |
| M6 Full Build (เทอม 2) | ~50 หุ้น, backfill 2020, เว็บครบ, LLM/RAG เต็ม | F1-04, F2-06, F2-07, F4-*, F5-03..05, F6-02, F7-02 |
| M7 Evaluation (เทอม 2) | ผ่านเป้าหมาย O1–O5 | F3-03, F5-06, F6-03, F7-03, QA-01..03 |
