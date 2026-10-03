# Stock News Sentiment — Design Documentation

เขียน spec ก่อนเขียนโค้ด และอัปเดตเอกสารใน PR เดียวกับโค้ดเสมอ
ต้นฉบับอ้างอิง: [Project Proposal](assets/Project_Proposal_Stock_News_Sentiment.pdf)

## เอกสารหลัก (อ่านตามลำดับ)
| ไฟล์ | เนื้อหา |
|---|---|
| [00-project-brief.md](00-project-brief.md) | โจทย์ต้นทาง สรุปจาก proposal |
| [01-project-charter.md](01-project-charter.md) | วัตถุประสงค์ 5 ข้อ ขอบเขต ทีม เกณฑ์เสร็จ |
| [02-problem-analysis.md](02-problem-analysis.md) | ปัญหาและสมมติฐานที่ต้องพิสูจน์ |
| [03-user-persona.md](03-user-persona.md) | persona ที่ใช้อ้างอิงทั้งโปรเจกต์ |
| [04-requirements.md](04-requirements.md) | FR / NFR แบบ MoSCoW |
| [05-data-design.md](05-data-design.md) | data contract, Kafka, ตาราง Iceberg |
| [06-system-architecture.md](06-system-architecture.md) | สถาปัตยกรรม และ **โครงสร้าง repository** |
| [07-sentiment-ai-design.md](07-sentiment-ai-design.md) | FinBERT, LLM summary, News RAG |
| [08-testing-evaluation.md](08-testing-evaluation.md) | วิธีวัดผลทุกวัตถุประสงค์ |
| [09-risks-limitations.md](09-risks-limitations.md) | ความเสี่ยงและข้อจำกัด |
| [10-roadmap-and-milestones.md](10-roadmap-and-milestones.md) | PoC เทอม 1, milestones |
| [11-ui-inventory.md](11-ui-inventory.md) | ทุกหน้าและ state ของเว็บแอป |

## เอกสารประกอบ
- [agents.md](agents.md) — **กฎการทำงาน: issue, ชื่อ branch, commit, PR** (บังคับใช้ทั้งคนและ AI)
- [CONTEXT.md](CONTEXT.md) — glossary
- [adr/](adr/) — Architecture Decision Records
- [issues/BOARD.md](issues/BOARD.md) — รายการงานทั้งหมดพร้อมชื่อ branch
- [assets/](assets/) — proposal และแผนภาพ
