# Scope, Non-Goals, and Success Criteria

## In Scope (Phase 1)
- Stock price ingestion for an initial pool of ~50 stocks.
- News / social ingestion from RSS and/or X/Twitter depending on accessible sources.
- Pretrained sentiment model integrated into the pipeline.
- Kafka streaming ingestion.
- Spark Structured Streaming for cleaning, transformation, aggregation, and joins.
- MinIO + Apache Iceberg + Nessie Lakehouse foundation.
- Web app: Stock Selection → Watchlist → Stock Detail Dashboard.
- Basic System Health view.

## Out of Scope (Phase 1)
- Separate production sentiment-model API service.
- RAG / chatbot.
- Full model monitoring / drift detection.
- Large-scale production authentication.
- Academic re-training/benchmarking of the sentiment model as the main project objective.

## Success Criteria
1. New price/news events can enter the streaming pipeline.
2. The pipeline produces structured, queryable outputs.
3. Sentiment outputs can be aggregated per ticker and time window.
4. Dashboard can display current sentiment and recent news.
5. Team can explain the end-to-end data flow and failure/recovery approach.
