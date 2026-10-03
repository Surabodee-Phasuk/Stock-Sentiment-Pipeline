# Testing Strategy

## Measurement per objective
| วัตถุประสงค์ | วิธีวัด | เป้าหมาย |
|---|---|---|
| 1. Lakehouse — query | Athena เทียบมี/ไม่มี partition | ≤ 5 วินาที |
| 1. Lakehouse — คุณภาพ | หาข่าวซ้ำในชั้น Cleaned, สาธิต time travel / schema evolution / reprocess จาก Raw | duplicate 0%, สาธิตครบ |
| 2. Streaming | เทียบเวลาเผยแพร่กับเวลาที่แสดงบนเว็บ; หยุดระบบกลางคันแล้วเปิดใหม่ | ≤ 15 นาที, ไม่สูญหาย 7 วัน |
| 3. FinBERT | ทีมติดป้าย 300 ข่าวแยกกัน เทียบกับผลโมเดล (Macro-F1, Cohen's kappa) | F1 ≥ 0.70 |
| 4. เว็บแอป | ผู้ใช้ 10 คนทำงานที่กำหนด + แบบสอบถาม SUS | ≥ 68 |
| 5. LLM สรุปข่าว | ตรวจ 50 สรุปเทียบข่าวต้นทาง (ไม่แต่งข้อมูล, สอดคล้อง FinBERT) | ≥ 90% |
| 5. News RAG | 50–100 คำถาม (ในและนอกขอบเขต) เทียบกับ LLM ไม่มี RAG | ≥ 90% |

## Unit tests
- data validation, ticker / timestamp normalization
- sentiment label mapping
- aggregation calculations

## Integration tests
- collector → Kafka, Kafka → Spark, Spark → Iceberg
- Athena query → web app response

## End-to-end
ข่าวใหม่ตามรอยได้: แหล่งข่าว → Kafka → Spark + FinBERT → Iceberg → Athena → เว็บ

## Reliability
- ข่าวซ้ำ, checkpoint/restart, field ว่าง, event ผิดรูป, timestamp ผิดปกติ

## Definition of Done
Feature เสร็จเมื่อโค้ดรัน ผ่าน acceptance criteria บันทึกผลทดสอบ และสมาชิกอีกคนรีวิวแล้ว
