# INFRA-02: AWS: S3 bucket, Glue database, Athena workgroup, IAM, budget alert

**Status:** in-progress  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.1, NFR-5, NFR-6  
**Branch:** `chore/infra-02-aws-foundation`  
**PR:** —

## งาน

- [x] S3 bucket สำหรับ warehouse และ checkpoint
- [x] Glue database `stock_sentiment`
- [x] Athena workgroup พร้อม result location
- [ ] IAM user/role แบบ least privilege (ตอนนี้ใช้ FullAccess 3 policy)
- [x] AWS budget alert (ยังไม่ได้ทดสอบส่งอีเมล)
- [ ] ตัดสินใจ scheduler สำหรับงาน batch (ADR ถ้าเลือกเครื่องมือใหม่)
- [ ] สคริปต์/คู่มือ setup ใน `infra/aws/`

## Acceptance criteria

- Athena query `SELECT 1` ผ่าน workgroup ได้
- budget alert ส่งอีเมลทดสอบได้
- ไม่มี credential ใน repo

## File scope

`infra/aws/`

## Evidence

- Athena `SELECT 1` ผ่าน workgroup `stock-sentiment` ได้ (M1, 2026-10-10)
- _(ยังขาด: ภาพอีเมลทดสอบ budget alert, IAM policy แบบ least privilege)_

## Comments

- **2026-10-11 (Claude, ขอโดย M1):** M1 สร้าง resource ด้วยมือแล้วเมื่อ 2026-10-10 บันทึกย้อนหลังไว้ที่นี่
  - Region: `ap-southeast-2` (Sydney) เพราะบัญชี AWS Free plan บังคับ region นี้
  - S3 bucket `stock-sentiment-lakehouse-surabodee` (warehouse ที่ `s3://stock-sentiment-lakehouse-surabodee/warehouse` ใช้ใน `infra/spark/spark-defaults.conf`)
  - Glue database `stock_sentiment`, Athena workgroup `stock-sentiment`
  - IAM user `surabodee-dev` ตั้งค่าผ่าน `aws configure` (key อยู่ใน `~/.aws` นอก repo)
  - Budget `Stock_Sentiment` $10/เดือน
  - ค้าง: เปิด MFA ให้ root account, ทดสอบอีเมล budget alert, ลดสิทธิ์ IAM ให้เหลือ least privilege, เลือก scheduler ของงาน batch, เขียนคู่มือ setup ใน `infra/aws/`
