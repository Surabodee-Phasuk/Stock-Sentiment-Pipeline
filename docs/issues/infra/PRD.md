# PRD: INFRA — Infrastructure & Repository Setup

เตรียมโครงสร้าง repo, AWS (S3 / Glue / Athena / budget alert), Kafka + Spark สำหรับพัฒนาในเครื่อง และ CI

**อ้างอิง:** NFR-5, NFR-6 ใน [docs/04-requirements.md](../../04-requirements.md)  
**Milestones:** M0, M1

## Issues

| # | งาน | Owner | Phase | Branch |
|---|---|---|---|---|
| [01](issues/01-project-structure.md) | โครงสร้าง repo, เอกสาร, ชื่อ branch และ workflow | M1+M2 | PoC (T1/2569) | `chore/infra-01-project-structure` |
| [02](issues/02-aws-foundation.md) | AWS: S3 bucket, Glue database, Athena workgroup, IAM, budget alert | M1 | PoC (T1/2569) | `chore/infra-02-aws-foundation` |
| [03](issues/03-local-kafka-spark.md) | Docker Compose: Kafka + Spark สำหรับพัฒนาในเครื่อง | M1 | PoC (T1/2569) | `chore/infra-03-local-kafka-spark` |
| [04](issues/04-ci-pipeline.md) | GitHub Actions: lint + unit test ทุก PR | M2 | PoC (T1/2569) | `chore/infra-04-ci-pipeline` |
