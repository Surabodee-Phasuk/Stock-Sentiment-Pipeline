# INFRA-02: AWS: S3 bucket, Glue database, Athena workgroup, IAM, budget alert

**Status:** todo  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.1, NFR-5, NFR-6  
**Branch:** `chore/infra-02-aws-foundation`  
**PR:** —

## งาน

- [ ] S3 bucket สำหรับ warehouse และ checkpoint
- [ ] Glue database `stock_sentiment`
- [ ] Athena workgroup พร้อม result location
- [ ] IAM user/role แบบ least privilege
- [ ] AWS budget alert
- [ ] ตัดสินใจ scheduler สำหรับงาน batch (ADR ถ้าเลือกเครื่องมือใหม่)
- [ ] สคริปต์/คู่มือ setup ใน `infra/aws/`

## Acceptance criteria

- Athena query `SELECT 1` ผ่าน workgroup ได้
- budget alert ส่งอีเมลทดสอบได้
- ไม่มี credential ใน repo

## File scope

`infra/aws/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
