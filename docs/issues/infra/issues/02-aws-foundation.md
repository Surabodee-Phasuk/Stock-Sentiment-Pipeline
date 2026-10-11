# INFRA-02: AWS: S3 bucket, Glue database, Athena workgroup, IAM, budget alert

**Status:** in-progress  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.1, NFR-5, NFR-6  
**Branch:** `chore/infra-02-aws-foundation`  
**PR:** —

## งาน

- [x] S3 bucket สำหรับ warehouse และ checkpoint (`stock-sentiment-lakehouse-surabodee`, region `ap-southeast-2`)
- [x] Glue database `stock_sentiment`
- [x] Athena workgroup พร้อม result location (`stock-sentiment`)
- [ ] IAM user/role แบบ least privilege — มี user `surabodee-dev` และเขียน `infra/aws/policy-dev.json` แล้ว แต่ยังใช้ FullAccess 3 ตัวอยู่
- [x] AWS budget alert (`Stock_Sentiment` $10/เดือน)
- [ ] ตัดสินใจ scheduler สำหรับงาน batch (ADR ถ้าเลือกเครื่องมือใหม่)
- [x] สคริปต์/คู่มือ setup ใน `infra/aws/` (`README.md`, `policy-dev.json`, `check.sh`)

## Acceptance criteria

- Athena query `SELECT 1` ผ่าน workgroup ได้
- budget alert ส่งอีเมลทดสอบได้
- ไม่มี credential ใน repo

## File scope

`infra/aws/`

## Evidence

- Athena `SELECT 1` ผ่าน workgroup `stock-sentiment`: สถานะ Completed ได้ผล `1` ใช้เวลา 178 ms (M1 ทดสอบผ่าน Console)
- ผล `bash infra/aws/check.sh`:
  ```
  _(วางผลรันที่นี่ ต้องจบด้วย "all checks passed" — ลบเลข account ออกก่อนวาง)_
  ```
- ไม่มี credential ใน repo: key อยู่ใน `~/.aws/` นอกโปรเจกต์, `policy-dev.json` ใช้ `ACCOUNT_ID` เป็น placeholder
- ยังไม่ผ่าน: budget alert ส่งอีเมลทดสอบ (ยังไม่ได้ทดสอบ)

## Comments
- 2026-10-10 (Claude, ขอโดย M1): resource ทั้งหมดสร้างด้วยมือผ่าน Console ที่ `ap-southeast-2` (Sydney) เพราะ Free plan บังคับ region นี้ คู่มือและค่าต่างๆ อยู่ใน `infra/aws/README.md` ที่ยังเหลือก่อนปิด: ถอด FullAccess แล้วใช้ `policy-dev.json` แทน, ทดสอบอีเมล budget, ตัดสินใจ scheduler และยืนยันว่าเปิด MFA ให้บัญชีหลักแล้ว
