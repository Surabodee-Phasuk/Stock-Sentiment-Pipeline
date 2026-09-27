# Testing Strategy

## Unit tests
- data validation
- ticker normalization
- timestamp normalization
- sentiment label mapping
- aggregation calculations

## Integration tests
- producer → Kafka
- Kafka → Spark
- Spark → Iceberg
- query → dashboard data response

## End-to-end test
A new news event should be traceable through:
Source → Kafka → Spark → sentiment → Iceberg → query → dashboard

## Reliability checks
- duplicate event handling
- checkpoint/restart behaviour
- missing/null fields
- malformed events
- late events / timestamp issues

## Definition of Done
A feature is Done only when code runs, acceptance criteria pass, tests are recorded, and the second member has reviewed the change.
