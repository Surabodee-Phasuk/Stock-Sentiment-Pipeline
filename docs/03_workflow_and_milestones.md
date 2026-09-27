# Development Workflow and Milestones

## Repository workflow
BACKLOG → TODO → IN PROGRESS → REVIEW → TESTING → DONE

Every task should define:
- Owner
- Milestone
- Dependencies
- Acceptance criteria
- Test evidence

## Milestones
### M0 — Planning Ready
- Project scope locked
- Architecture locked enough to start
- Data contracts agreed
- Task ownership agreed

### M1 — Infrastructure Ready
- Kafka, MinIO, Nessie running locally
- Topics created
- Basic producer/consumer proof works

### M2 — Ingestion Ready
- Stock price events enter Kafka
- News events enter Kafka
- Events follow agreed schema

### M3 — Processing Ready
- Spark reads Kafka
- Cleaning/transform works
- Sentiment result produced
- Windowed aggregation works

### M4 — Lakehouse Ready
- Raw / cleaned / aggregated tables exist
- Iceberg tables are queryable
- Nessie catalog works
- Upsert/idempotency path tested

### M5 — Application Ready
- Stock Selection works
- Watchlist works
- Detail Dashboard works
- Sentiment is visible without hardcoded demo values

### M6 — End-to-End Ready
News/price → Kafka → Spark → Sentiment → Iceberg → Query → Dashboard

## 11-week planning view
| Week | Focus | Member 1 | Member 2 |
|---|---|---|---|
| 1 | Planning | architecture/data platform docs | UI/data contract docs |
| 2 | Infra + mock UI | Kafka/MinIO/Nessie | UI prototype |
| 3 | Ingestion | stock API + Kafka | news schema/connectors |
| 4 | Streaming | Kafka integration/reliability | Spark cleaning |
| 5 | Processing | streaming reliability | sentiment + aggregation |
| 6 | Lakehouse | Iceberg/Nessie | dashboard data outputs |
| 7 | Query | query performance/data access | dashboard queries |
| 8 | Application | integration support | web app |
| 9 | Watchlist + scale test | backend/data performance | UI + sentiment UX |
| 10 | Testing | pipeline/integration tests | UI/E2E tests |
| 11 | Finalize | deployment/system docs | UI/demo/presentation |
