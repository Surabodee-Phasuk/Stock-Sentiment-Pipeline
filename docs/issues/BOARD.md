# BOARD — Stock News Sentiment

รายการงานทั้งหมดพร้อมชื่อ branch ที่กำหนดล่วงหน้า **ใช้ชื่อ branch ตามตารางนี้เท่านั้น** (กฎใน [../agents.md](../agents.md))

Status: `todo` · `in-progress` · `in-review` · `done` · `wontfix` — อัปเดตแถวนี้ใน PR เดียวกับงาน

## INFRA — Infrastructure & Repository Setup
PRD: [infra/PRD.md](infra/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [INFRA-01](infra/issues/01-project-structure.md) | โครงสร้าง repo, เอกสาร, ชื่อ branch และ workflow | M1+M2 | PoC (T1/2569) | done | `chore/infra-01-project-structure` | [#2](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/2) |
| [INFRA-02](infra/issues/02-aws-foundation.md) | AWS: S3 bucket, Glue database, Athena workgroup, IAM, budget alert | M1 | PoC (T1/2569) | todo | `chore/infra-02-aws-foundation` | — |
| [INFRA-03](infra/issues/03-local-kafka-spark.md) | Docker Compose: Kafka + Spark สำหรับพัฒนาในเครื่อง | M1 | PoC (T1/2569) | todo | `chore/infra-03-local-kafka-spark` | — |
| [INFRA-04](infra/issues/04-ci-pipeline.md) | GitHub Actions: lint + unit test ทุก PR | M2 | PoC (T1/2569) | todo | `chore/infra-04-ci-pipeline` | — |

## F1 — Ingestion — ข่าวและราคาปิด
PRD: [f1-ingestion/PRD.md](f1-ingestion/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [F1-01](f1-ingestion/issues/01-news-collector.md) | News collector RSS / News API → Kafka (10 หุ้น) | M1 | PoC (T1/2569) | todo | `feat/f1-01-news-collector` | — |
| [F1-02](f1-ingestion/issues/02-yahoo-daily-close.md) | Yahoo Finance daily close collector (10 หุ้น) | M1 | PoC (T1/2569) | todo | `feat/f1-02-yahoo-daily-close` | — |
| [F1-03](f1-ingestion/issues/03-multi-source-news.md) | รวมหลายแหล่งข่าวและตัดซ้ำเบื้องต้นที่ collector | M1 | PoC (T1/2569) | todo | `feat/f1-03-multi-source-news` | — |
| [F1-04](f1-ingestion/issues/04-backfill-2020.md) | Backfill ข่าวและราคาปิดย้อนหลังตั้งแต่ปี 2020 สำหรับ ~50 หุ้น | M1 | Full (T2/2570) | todo | `feat/f1-04-backfill-2020` | — |

## F2 — Lakehouse — S3 + Iceberg
PRD: [f2-lakehouse/PRD.md](f2-lakehouse/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [F2-01](f2-lakehouse/issues/01-iceberg-tables.md) | DDL ตาราง Iceberg ทั้งสามชั้นใน Glue | M1 | PoC (T1/2569) | todo | `feat/f2-01-iceberg-tables` | — |
| [F2-02](f2-lakehouse/issues/02-kafka-to-raw-streaming.md) | Spark Structured Streaming: Kafka → `raw_news` พร้อม checkpoint | M1 | PoC (T1/2569) | todo | `feat/f2-02-kafka-to-raw-streaming` | — |
| [F2-03](f2-lakehouse/issues/03-dedup-to-cleaned.md) | ตัดข่าวซ้ำ: `raw_news` → `clean_news` ด้วย MERGE | M1 | PoC (T1/2569) | todo | `feat/f2-03-dedup-to-cleaned` | — |
| [F2-04](f2-lakehouse/issues/04-price-batch-load.md) | Spark batch: ราคาปิด → `raw_daily_price` / `daily_price` | M2 | PoC (T1/2569) | todo | `feat/f2-04-price-batch-load` | — |
| [F2-05](f2-lakehouse/issues/05-time-travel-schema-evolution.md) | สาธิต time travel และ schema evolution | M1 | PoC (T1/2569) | todo | `exp/f2-05-time-travel-schema-evolution` | — |
| [F2-06](f2-lakehouse/issues/06-scale-50-tickers.md) | ขยาย pipeline เป็น ~50 หุ้นและข้อมูลตั้งแต่ 2020 | M1 | Full (T2/2570) | todo | `feat/f2-06-scale-50-tickers` | — |
| [F2-07](f2-lakehouse/issues/07-partition-benchmark.md) | Benchmark partition และล็อก partition spec | M1 | Full (T2/2570) | todo | `test/f2-07-partition-benchmark` | — |

## F3 — Sentiment — FinBERT
PRD: [f3-sentiment/PRD.md](f3-sentiment/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [F3-01](f3-sentiment/issues/01-finbert-streaming.md) | FinBERT ใน Spark Structured Streaming → `news_sentiment` | M2 | PoC (T1/2569) | todo | `feat/f3-01-finbert-streaming` | — |
| [F3-02](f3-sentiment/issues/02-finbert-poc-benchmark.md) | PoC: F1 บน 100 ข่าว และ throughput | M2 | PoC (T1/2569) | todo | `exp/f3-02-finbert-poc-benchmark` | — |
| [F3-03](f3-sentiment/issues/03-goldset-300-eval.md) | Gold set 300 ข่าว: ติดป้ายแยกกัน, Cohen's kappa, Macro-F1 | M1+M2 | Full (T2/2570) | todo | `test/f3-03-goldset-300-eval` | — |
| [F3-04](f3-sentiment/issues/04-reprocess-from-raw.md) | Reprocess sentiment ทั้งหมดจาก Raw เมื่อเปลี่ยน `model_version` | M2 | PoC (T1/2569) | todo | `feat/f3-04-reprocess-from-raw` | — |

## F4 — Aggregation & Serving API
PRD: [f4-aggregation/PRD.md](f4-aggregation/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [F4-01](f4-aggregation/issues/01-sentiment-daily.md) | Spark batch: `sentiment_daily` (sentiment รายวัน + ราคาปิด) | M2 | Full (T2/2570) | todo | `feat/f4-01-sentiment-daily` | — |
| [F4-02](f4-aggregation/issues/02-query-api.md) | API layer: endpoint สำหรับ Search / Home / Stock Detail ผ่าน Athena | M2 | Full (T2/2570) | todo | `feat/f4-02-query-api` | — |

## F5 — Web App
PRD: [f5-webapp/PRD.md](f5-webapp/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [F5-01](f5-webapp/issues/01-ui-prototype.md) | Prototype ครบ 4 หน้า + ตัดสินใจเทคโนโลยีเว็บ (ADR) | M2 | PoC (T1/2569) | todo | `feat/f5-01-ui-prototype` | — |
| [F5-02](f5-webapp/issues/02-stock-detail-real-data.md) | Stock Detail PoC ดึงข้อมูลจริงจาก Athena | M2 | PoC (T1/2569) | todo | `feat/f5-02-stock-detail-real-data` | — |
| [F5-03](f5-webapp/issues/03-search-page.md) | หน้า Search | M2 | Full (T2/2570) | todo | `feat/f5-03-search-page` | — |
| [F5-04](f5-webapp/issues/04-home-watchlist.md) | หน้า Home (Watchlist) | M2 | Full (T2/2570) | todo | `feat/f5-04-home-watchlist` | — |
| [F5-05](f5-webapp/issues/05-stock-detail-full.md) | หน้า Stock Detail เต็ม + disclaimer | M2 | Full (T2/2570) | todo | `feat/f5-05-stock-detail-full` | — |
| [F5-06](f5-webapp/issues/06-sus-usability-test.md) | ทดสอบผู้ใช้ 10 คน + SUS | M2 | Full (T2/2570) | todo | `test/f5-06-sus-usability-test` | — |

## F6 — LLM Summary
PRD: [f6-llm-summary/PRD.md](f6-llm-summary/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [F6-01](f6-llm-summary/issues/01-llm-summary-poc.md) | PoC: สรุป 5 ชิ้น ตรวจด้วยคน + ค่าใช้จ่ายต่อชิ้น + ADR เลือก LLM | M1+M2 | PoC (T1/2569) | todo | `exp/f6-01-llm-summary-poc` | — |
| [F6-02](f6-llm-summary/issues/02-llm-summary-service.md) | สรุปรายวันอัตโนมัติ + cache + แสดงใน Stock Detail | M1+M2 | Full (T2/2570) | todo | `feat/f6-02-llm-summary-service` | — |
| [F6-03](f6-llm-summary/issues/03-llm-summary-eval-50.md) | ประเมิน 50 สรุป | M1+M2 | Full (T2/2570) | todo | `test/f6-03-llm-summary-eval-50` | — |

## F7 — News RAG (Ask AI)
PRD: [f7-news-rag/PRD.md](f7-news-rag/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [F7-01](f7-news-rag/issues/01-rag-poc.md) | PoC: ตอบ 10 คำถามพร้อมแหล่งอ้างอิง + ADR vector store | M1+M2 | PoC (T1/2569) | todo | `exp/f7-01-rag-poc` | — |
| [F7-02](f7-news-rag/issues/02-ask-ai-page.md) | หน้า Ask AI + guardrail นอกขอบเขต | M1+M2 | Full (T2/2570) | todo | `feat/f7-02-ask-ai-page` | — |
| [F7-03](f7-news-rag/issues/03-rag-eval.md) | ประเมิน 50–100 คำถาม เทียบ LLM ไม่มี RAG | M1+M2 | Full (T2/2570) | todo | `test/f7-03-rag-eval` | — |

## QA — Quality, Reliability & Final Delivery
PRD: [qa/PRD.md](qa/PRD.md)

| ID | งาน | Owner | Phase | Status | Branch | PR |
|---|---|---|---|---|---|---|
| [QA-01](qa/issues/01-e2e-latency.md) | วัด end-to-end latency (เผยแพร่ → เว็บ) | M1+M2 | Full (T2/2570) | todo | `test/qa-01-e2e-latency` | — |
| [QA-02](qa/issues/02-seven-day-reliability.md) | รันต่อเนื่อง 7 วัน + หยุดกลางคันแล้วกู้จาก checkpoint | M1 | Full (T2/2570) | todo | `test/qa-02-seven-day-reliability` | — |
| [QA-03](qa/issues/03-final-report-demo.md) | รายงานฉบับสมบูรณ์ demo flow และ tag `v1.0` | M1+M2 | Full (T2/2570) | todo | `docs/qa-03-final-report-demo` | — |
