# 08 — Testing & Evaluation

## วัดผลตามวัตถุประสงค์
| วัตถุประสงค์ | วิธีวัด | ตัวชี้วัด | เป้าหมาย | Issue |
|---|---|---|---|---|
| O1 Lakehouse | Query ข่าวคู่ราคาผ่าน Athena เทียบมี/ไม่มี partition | เวลา query, ข้อมูลที่สแกน | ≤ 5 วินาที | F2-07 |
| O1 Lakehouse | หาข่าวซ้ำในชั้น Cleaned, สาธิต time travel / schema evolution / reprocess | duplicate rate, ผลการสาธิต | 0%, ครบทุกข้อ | F2-03, F2-05, F3-04 |
| O2 Streaming | เทียบเวลาเผยแพร่กับเวลาที่แสดงบนเว็บ; หยุดระบบกลางคันแล้วเปิดใหม่ | latency, ข่าวสูญหาย | ≤ 15 นาที, ไม่สูญหาย 7 วัน | QA-01, QA-02 |
| O3 FinBERT | ทีมติดป้าย 300 ข่าวแยกกัน เทียบกับโมเดล | Macro-F1, Cohen's kappa | F1 ≥ 0.70 | F3-03 |
| O4 เว็บแอป | ผู้ใช้ 10 คนทำงานที่กำหนด + แบบสอบถาม | SUS | ≥ 68 | F5-06 |
| O5 LLM | ตรวจ 50 สรุปเทียบข่าวต้นทาง | ไม่แต่งข้อมูล, สอดคล้อง FinBERT | ≥ 90% | F6-03 |
| O5 RAG | 50–100 คำถาม (ใน/นอกขอบเขต) เทียบ LLM ไม่มี RAG | ค้นถูกหุ้น, อ้างอิงถูก, ปฏิเสธถูก | ≥ 90% | F7-03 |

## ระดับการทดสอบ
- **Unit** (`pytest`, อยู่ข้างโค้ดใน `<module>/tests/`): validation, normalize ticker/timestamp, `news_id` hashing, label mapping, aggregation
- **Integration** (`tests/integration/`): collector → Kafka, Kafka → Spark → Iceberg, Athena → API
- **E2E** (`tests/e2e/`): ข่าวใหม่ตามรอยได้ตั้งแต่แหล่งข่าวจนถึงหน้าเว็บ
- **Reliability** (`tests/reliability/`): ข่าวซ้ำ, checkpoint/restart, field ว่าง, event ผิดรูป, timestamp ผิดปกติ

## หลักฐาน
ผลวัดทุกตัวบันทึกใน issue ที่เกี่ยวข้อง (หัวข้อ `## Evidence`) พร้อม query / สคริปต์ที่รันซ้ำได้
