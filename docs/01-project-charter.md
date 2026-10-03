# 01 — Project Charter

## เป้าหมาย (5 วัตถุประสงค์)
ค่าเป้าหมายเป็นค่าเบื้องต้น จะยืนยันหลังทำ PoC ในเทอม 1

| # | วัตถุประสงค์ | เป้าหมาย |
|---|---|---|
| O1 | Data Lakehouse บน S3 + Iceberg เก็บข่าว ผล sentiment และราคาปิดของ ~50 หุ้น แบ่งชั้น Raw / Cleaned / Aggregated | ข่าว streaming กับราคา batch อยู่ในตารางชุดเดียวกันและ query ผ่าน Athena ได้ (≤ 5 วินาที), duplicate rate = 0% ในชั้น Cleaned, reprocess sentiment จาก Raw ได้, สาธิต time travel และ schema evolution ได้จริง |
| O2 | Pipeline รับข่าวใกล้เคียงเวลาจริงด้วย Kafka + Spark Structured Streaming | ข่าวใหม่แสดงบนเว็บภายใน 15 นาที, ทำงานต่อเนื่อง ≥ 7 วันไม่สูญหายข่าว (กู้คืนจาก checkpoint ได้) |
| O3 | จำแนก sentiment รายข่าว Positive / Neutral / Negative ด้วย FinBERT | Macro-F1 ≥ 0.70 บนชุดข่าว 300 ข่าวที่ทีมติดป้ายเอง |
| O4 | เว็บแอปแสดงภาพรวม sentiment ราคาปิดรายวัน และข่าวล่าสุดของหุ้นที่ผู้ใช้เลือก | หน้า Search, Home, Stock Detail ทำงานครบ; ผู้ใช้ 10 คน SUS ≥ 68 |
| O5 | LLM สรุปข่าวประจำวัน + News RAG | สรุป 50 ชิ้นไม่แต่งข้อมูล ≥ 90%; คำถาม 50–100 ข้อ ค้นถูกหุ้น อ้างอิงถูก ปฏิเสธนอกขอบเขตได้ ≥ 90% |

## ขอบเขต
| ด้าน | อยู่ในขอบเขต | ไม่อยู่ในขอบเขต |
|---|---|---|
| หุ้น | หุ้นสหรัฐฯ ~50 ตัว (Tech, Auto, Energy, Space) | หุ้นไทย, คริปโต |
| ข่าว | ข่าวภาษาอังกฤษ ย้อนหลังตั้งแต่ 2020 และข่าวใหม่ทุก 5–15 นาที | โพสต์โซเชียล (X, Reddit, StockTwits) |
| ราคา | ราคาปิดรายวันจาก Yahoo Finance ตั้งแต่ 2020 | ราคาระหว่างวัน |
| การวิเคราะห์ | sentiment รายข่าวและภาพรวมรายหุ้นรายวัน เทียบทิศทางราคาปิด | ทำนายราคา, คำแนะนำซื้อขาย |
| เว็บแอป | Search, Home (Watchlist), Stock Detail, Ask AI | แอปมือถือ |
| AI | LLM สรุปข่าว, RAG ตอบเฉพาะหุ้นในระบบพร้อมแหล่งอ้างอิง | ฝึกโมเดลภาษาใหม่เอง |

## ทีม
| ชื่อ | รหัส | ตัวย่อใน issue | Primary |
|---|---|---|---|
| สุรบดี ผาสุข | 6609650707 | **M1** | Data Platform / Ingestion / Lakehouse |
| รพินทร์ นะราช | 6609650624 | **M2** | Processing / Sentiment / Web App |

ใช้ Primary Owner + Secondary Owner: ทุกคนต้องเข้าใจ pipeline ทั้งระบบพอจะ review, debug และนำเสนอได้ งาน LLM / RAG เป็นงานร่วม

## เกณฑ์ว่าเสร็จ (Definition of Done ของโครงงาน)
- **เทอม 1:** ทุกแถวในตาราง PoC ([10-roadmap-and-milestones.md](10-roadmap-and-milestones.md)) ผ่านเกณฑ์ และมีหลักฐานใน issue
- **เทอม 2:** ผ่านเป้าหมาย O1–O5 ทั้งหมด พร้อมผลวัดตาม [08-testing-evaluation.md](08-testing-evaluation.md)
