# Architecture Decision Log

## DEC-001 — Data Engineering first
Phase 1 prioritizes the end-to-end data pipeline and lakehouse before advanced AI features.

## DEC-002 — Initial stock pool ~50
The initial scope is ~50 stocks to keep the 11-week Phase 1 manageable; architecture is designed for later expansion.

## DEC-003 — Sentiment-first UX
The dashboard emphasizes positive / neutral / negative news sentiment rather than a dense technical-analysis dashboard.

## DEC-004 — Separate selection, watchlist, and detail
The web flow is Stock Selection → Watchlist → Stock Detail Dashboard.

## DEC-005 — Primary Owner + Secondary Owner
Each team member owns a subsystem but both members must understand the full pipeline for integration, debugging, and presentation.

## Open decisions before coding
- Final stock price API
- Final news/social sources that are technically accessible
- Final sentiment model
- Streamlit vs React + API
- Dremio vs Trino vs direct query approach
- Whether Airflow is needed in Phase 1 or remains optional
- Exact Iceberg partition specification after sample workload testing
