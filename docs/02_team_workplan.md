# 2-Person Work Plan

## Ownership model
Use “Primary Owner + Secondary Owner” rather than splitting the system into isolated halves. Each member owns a subsystem but must understand the full pipeline well enough to review, debug, and present it.

## Member 1 — สุรบดี ผาสุข
Primary: Data Platform / Ingestion / Lakehouse

Responsibilities:
- Docker/local infrastructure
- Kafka topics and producers
- Stock price ingestion
- News ingestion support / source connectors
- MinIO / Iceberg / Nessie
- Partitioning, upsert/idempotency
- Basic pipeline reliability and health checks

Secondary knowledge:
- Spark streaming
- Sentiment data contract
- Dashboard query requirements

## Member 2 — รพินทร์ นะราช
Primary: Processing / Sentiment / Web App

Responsibilities:
- Spark Structured Streaming transformations
- Data cleaning and normalization
- Sentiment model integration
- Sentiment aggregation
- Query/data-serving layer
- Stock Selection / Watchlist / Detail Dashboard
- UI/UX and end-to-end UI testing

Secondary knowledge:
- Kafka basics
- Iceberg/Nessie data layout
- Data quality and pipeline health

## Shared responsibilities
- Architecture decisions
- Data schema review
- Integration testing
- Git/GitHub workflow
- Final presentation and demo
