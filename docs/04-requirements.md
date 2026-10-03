# 04 — Requirements

Priority แบบ MoSCoW: **M** = Must, **S** = Should, **C** = Could. ทุก issue ต้องอ้าง ID ในหน้านี้ใน field `Refs`

## Functional Requirements

### FR-1 Ingestion
| ID | Requirement | P |
|---|---|---|
| FR-1.1 | ดึงข่าวภาษาอังกฤษจาก RSS / News API ทุก 5–15 นาที และส่งเข้า Kafka topic `stock-news` | M |
| FR-1.2 | ดึงราคาปิดรายวันจาก Yahoo Finance วันละครั้ง (เว้นจังหวะเพื่อไม่ให้โดนบล็อก) | M |
| FR-1.3 | รายชื่อหุ้น ~50 ตัว (PoC 10 ตัว) จัดเก็บเป็นไฟล์ config เดียว | M |
| FR-1.4 | ดึงข่าวและราคาย้อนหลังตั้งแต่ปี 2020 (backfill) | S |
| FR-1.5 | รวมหลายแหล่งข่าวเพื่อลดผลจาก rate limit | S |

### FR-2 Lakehouse
| ID | Requirement | P |
|---|---|---|
| FR-2.1 | ตาราง Iceberg บน S3 แบ่งชั้น Raw / Cleaned / Aggregated ลงทะเบียนใน Glue | M |
| FR-2.2 | Spark Structured Streaming อ่าน Kafka แล้วเขียนชั้น Raw พร้อม checkpoint | M |
| FR-2.3 | ชั้น Cleaned ไม่มีข่าวซ้ำ (duplicate rate = 0%) | M |
| FR-2.4 | ราคาปิด batch และข่าว streaming อยู่ในตารางชุดเดียวกัน query ร่วมผ่าน Athena ได้ | M |
| FR-2.5 | สาธิต time travel และ schema evolution | M |
| FR-2.6 | ประมวลผล sentiment ใหม่ทั้งหมดจากชั้น Raw เมื่อเปลี่ยนโมเดล โดยไม่ดึงข่าวใหม่ | M |

### FR-3 Sentiment
| ID | Requirement | P |
|---|---|---|
| FR-3.1 | จำแนกข่าวด้วย FinBERT เป็น positive / neutral / negative พร้อม score และ `model_version` | M |
| FR-3.2 | ชุดข่าว 300 ข่าวที่ทีมติดป้ายแยกกัน (gold set) | M |
| FR-3.3 | ภาพรวม sentiment รายหุ้นรายวันในชั้น Aggregated เทียบกับราคาปิด | M |

### FR-4 Web App
| ID | Requirement | P |
|---|---|---|
| FR-4.1 | หน้า Search: ค้นหา/กรองหุ้นตาม ticker ชื่อ กลุ่มอุตสาหกรรม | M |
| FR-4.2 | หน้า Home (Watchlist): การ์ดหุ้นที่เลือก แสดง sentiment badge, สัดส่วน, ราคาปิด, เวลาอัปเดต | M |
| FR-4.3 | หน้า Stock Detail: กราฟ sentiment รายวันเทียบราคาปิด + ข่าวล่าสุดพร้อมแหล่ง/คะแนน | M |
| FR-4.4 | หน้า Ask AI (แท็บในเมนูล่าง) | M (เทอม 2) |
| FR-4.5 | ข้อความชัดเจนว่าไม่ใช่คำแนะนำการลงทุน | M |

### FR-5 LLM Summary
| ID | Requirement | P |
|---|---|---|
| FR-5.1 | สรุปข่าวประจำวันของแต่ละหุ้น 3–5 ประโยค พร้อมเหตุผลของ sentiment ใช้เฉพาะข่าวในชั้น Cleaned | M |
| FR-5.2 | แสดงในหน้า Stock Detail ข้างการ์ด sentiment | M |

### FR-6 News RAG
| ID | Requirement | P |
|---|---|---|
| FR-6.1 | ค้นข่าวเฉพาะหุ้นที่ถาม ตอบพร้อมแหล่งอ้างอิง (headline, source, time) | M |
| FR-6.2 | ปฏิเสธคำถามนอกขอบเขต (หุ้นนอกระบบ, คำแนะนำซื้อขาย, เรื่องอื่น) | M |

## Non-functional Requirements
| ID | Requirement | เป้าหมาย |
|---|---|---|
| NFR-1 | Latency end-to-end (เผยแพร่ → แสดงบนเว็บ) | ≤ 15 นาที |
| NFR-2 | ความต่อเนื่อง / ไม่สูญหายข่าว | ≥ 7 วัน, กู้คืนจาก checkpoint |
| NFR-3 | Athena query ข่าวคู่ราคา | ≤ 5 วินาที |
| NFR-4 | Idempotency | ข่าวซ้ำไม่ถูกเขียนซ้ำในชั้น Cleaned (MERGE) |
| NFR-5 | ค่าใช้จ่าย | ตั้ง AWS budget alert, วัดค่าใช้จ่าย LLM ต่อชิ้น/ต่อคำถาม |
| NFR-6 | Secrets | ไม่ commit API key / AWS credential (ใช้ `.env` ที่ gitignore) |
| NFR-7 | Usability | SUS ≥ 68 |
