# 06 — System Architecture

ข้อมูลเข้า 2 ทาง แต่ลงตาราง Iceberg ชุดเดียวกัน ซึ่งเป็นสิ่งที่โครงงานต้องพิสูจน์ว่า Data Lakehouse ทำงานได้จริง

![Architecture](assets/system-architecture.png)

*แผนภาพจาก [Project Proposal](assets/Project_Proposal_Stock_News_Sentiment.pdf) หน้า 3*

```mermaid
flowchart LR
    Y[Yahoo Finance\nราคาปิดวันละครั้ง] --> SB[Spark batch\nราคา + reprocess]
    N[RSS / News API\nทุก 5-15 นาที] --> K[Kafka] --> SS[Spark Structured Streaming\n+ FinBERT]
    subgraph LH[S3 + Apache Iceberg]
      R[Raw] --> C[Cleaned] --> A[Aggregated]
    end
    SB --> LH
    SS --> R
    LH --> G[Glue + Athena]
    G --> API[API] --> W[Web App]
    C --> AI[LLM + News RAG]
    AI --> API
```

- **Streaming:** ข่าวใหม่ผ่าน Kafka และ Spark Structured Streaming ทุก 5–15 นาที
- **Batch:** ราคาปิดรายวันจาก Yahoo Finance วันละครั้ง และงาน reprocess sentiment จากชั้น Raw เมื่อเปลี่ยนโมเดล
- **Serving:** เว็บแอปอ่านชั้น Aggregated ผ่าน Athena; LLM และ RAG ใช้ข่าวจากชั้น Cleaned

## Environment (PoC)
| ส่วน | ค่า | Issue |
|---|---|---|
| AWS region | `ap-southeast-2` (Sydney) เพราะบัญชี AWS Free plan บังคับ | INFRA-02 |
| S3 bucket | `stock-sentiment-lakehouse-surabodee`, Iceberg warehouse ที่ `s3://stock-sentiment-lakehouse-surabodee/warehouse` | INFRA-02 |
| Glue database | `stock_sentiment` (Spark เรียก catalog นี้ว่า `glue`) | INFRA-02 |
| Athena workgroup | `stock-sentiment` | INFRA-02 |
| Kafka (ในเครื่อง) | Kafka 4.3.1 แบบ KRaft โหนดเดียว เชื่อมจากเครื่องที่ `localhost:9092` และจาก container ที่ `kafka:19092` | INFRA-03 |
| Spark (ในเครื่อง) | Spark 4.0.4 local mode + Iceberg 1.12.0 ใน Docker | INFRA-03 |

วิธีเปิดใช้: [infra/README.md](../infra/README.md)

## โครงสร้าง repository
ทุกโฟลเดอร์ถูกสร้างไว้แล้วพร้อม README บอกขอบเขต ห้ามสร้างโฟลเดอร์ระดับบนสุดใหม่โดยไม่มี ADR

```
Stock-Sentiment-Pipeline/
├── AGENTS.md / CLAUDE.md   # ชี้ไป docs/agents.md (กฎสำหรับคนและ AI)
├── .github/                # PR template, issue template, CI
├── config/                 # tickers.yaml, ค่าคงที่ร่วม
├── infra/                  # docker-compose (Kafka, Spark local), AWS setup scripts
├── ingestion/              # news collector → Kafka, Yahoo Finance daily close
├── streaming/              # Spark Structured Streaming: Kafka → Raw → Cleaned + FinBERT
├── batch/                  # Spark batch: ราคาปิด, aggregation รายวัน, reprocess
├── lakehouse/              # DDL ตาราง Iceberg, Athena queries, demo time travel
├── sentiment/              # FinBERT wrapper, gold set, evaluation scripts
├── ai/                     # LLM summary + News RAG (เทอม 2)
├── webapp/                 # เว็บแอป + API layer
├── tests/                  # integration / e2e / reliability tests
└── docs/                   # เอกสารนี้
```

| โฟลเดอร์ | Primary owner | Feature |
|---|---|---|
| `infra/`, `config/` | M1 | INFRA |
| `ingestion/` | M1 | F1 |
| `lakehouse/`, `streaming/` (Raw/Cleaned) | M1 | F2 |
| `sentiment/`, FinBERT ใน `streaming/` | M2 | F3 |
| `batch/` | M2 | F4 |
| `webapp/` | M2 | F5 |
| `ai/` | M1 + M2 | F6, F7 |
| `tests/` | ทุกคน | QA |

## Request flow (Stock Detail)
1. ผู้ใช้เปิด `/stock/RKLB`
2. API query Athena: `sentiment_daily` + `daily_price` (30 วัน) และ `clean_news` JOIN `news_sentiment` (ข่าวล่าสุด 20 ข่าว)
3. (เทอม 2) API ดึงสรุป LLM ของวันนั้นจาก cache
4. Web App แสดงผล
