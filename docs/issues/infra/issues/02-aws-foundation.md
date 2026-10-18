# INFRA-02: AWS: S3 bucket, Glue database, Athena workgroup, IAM, budget alert

**Status:** done  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** FR-2.1, NFR-5, NFR-6  
**Branch:** `chore/infra-02-aws-foundation`  
**PR:** [#22](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/22)

## งาน

- [x] S3 bucket สำหรับ warehouse และ checkpoint (`stock-sentiment-lakehouse-surabodee`, region `ap-southeast-2`)
- [x] Glue database `stock_sentiment`
- [x] Athena workgroup พร้อม result location (`stock-sentiment`)
- [x] IAM user/role แบบ least privilege — user `surabodee-dev` ใช้เฉพาะ policy `StockSentimentDev` (จาก `infra/aws/policy-dev.json`) ถอด FullAccess ทั้ง 3 ตัวออกแล้ว
- [x] AWS budget alert (`Stock_Sentiment` $10/เดือน)
- [x] ตัดสินใจ scheduler สำหรับงาน batch (ADR ถ้าเลือกเครื่องมือใหม่) — PoC สั่งรันเองวันละครั้ง ไม่เพิ่มเครื่องมือใหม่จึงไม่มี ADR
- [x] สคริปต์/คู่มือ setup ใน `infra/aws/` (`README.md`, `policy-dev.json`, `check.sh`)

## Acceptance criteria

- Athena query `SELECT 1` ผ่าน workgroup ได้
- budget alert ส่งอีเมลทดสอบได้
- ไม่มี credential ใน repo

## File scope

`infra/aws/`

## Evidence

- Athena `SELECT 1` ผ่าน workgroup `stock-sentiment`: สถานะ Completed ได้ผล `1` ใช้เวลา 178 ms (M1 ทดสอบผ่าน Console)
- ผล `bash infra/aws/check.sh` หลังถอด FullAccess (2026-10-18) — สิทธิ์เหลือแค่ `StockSentimentDev`:
  ```
  == identity
  <ACCOUNT_ID>    arn:aws:iam::<ACCOUNT_ID>:user/surabodee-dev

  == s3: list s3://stock-sentiment-lakehouse-surabodee
                             PRE athena-results/

  == glue: database stock_sentiment
  stock_sentiment

  == athena: workgroup stock-sentiment result location
  s3://stock-sentiment-lakehouse-surabodee/athena-results/

  == athena: SELECT 1
  1

  all checks passed
  ```
- สิทธิ์ `StockSentimentDev` พอสำหรับ Spark + Iceberg: `infra/spark/smoke_iceberg.py` (INFRA-03) สร้าง/เขียน/อ่าน/ลบตารางบน S3 ผ่าน Glue ได้ → `iceberg smoke test passed` (2026-10-18)
- MFA: เปิดแล้วที่ AWS Builder ID ของบัญชีหลัก (Moonshot Mode ล็อกอินผ่าน Google) และเปิด 2-Step Verification ที่บัญชี Google
- ไม่มี credential ใน repo: key อยู่ใน `~/.aws/` นอกโปรเจกต์, `policy-dev.json` ใช้ `ACCOUNT_ID` เป็น placeholder
- budget alert ส่งอีเมลทดสอบ: **ทดสอบไม่ได้บน Free plan** — หน้า Billing แสดง "No charges while on the free plan", Amount due $0.00, month-to-date $0.00 (ทุกการใช้งานถูกหักจากเครดิต) จึงไม่มีค่าใช้จ่ายจริงให้เกินเกณฑ์ ตั้ง budget `Stock_Sentiment` $10/เดือนไว้แล้ว และใช้การดู Credits remaining ในหน้า Billing แทน (2026-10-18: เหลือ $120.00, หมดอายุ 8 เม.ย. 2027)

## Comments
- 2026-10-10 (Claude, ขอโดย M1): resource ทั้งหมดสร้างด้วยมือผ่าน Console ที่ `ap-southeast-2` (Sydney) เพราะ Free plan บังคับ region นี้ คู่มือและค่าต่างๆ อยู่ใน `infra/aws/README.md` ที่ยังเหลือก่อนปิด: ถอด FullAccess แล้วใช้ `policy-dev.json` แทน, ทดสอบอีเมล budget, ตัดสินใจ scheduler และยืนยันว่าเปิด MFA ให้บัญชีหลักแล้ว
- 2026-10-17 (Claude, ขอโดย M1): PR #22 merge เข้า `main` แล้วเมื่อ 2026-10-11 แต่ยังคง `in-progress` เพราะเหลืองานค้าง: ถอด FullAccess → `policy-dev.json`, ทดสอบอีเมล budget, ตัดสินใจ scheduler, ยืนยัน MFA บัญชีหลัก และวางผล `check.sh` ใน Evidence
- 2026-10-18 (Claude, ขอโดย M1): ปิด issue — ถอด FullAccess แล้ว `check.sh` และ `smoke_iceberg.py` ยังผ่าน, เปิด MFA แล้ว, scheduler ช่วง PoC = สั่งรันเอง ข้อยกเว้น: ทดสอบอีเมล budget ไม่ได้เพราะ Free plan ไม่มีค่าใช้จ่ายจริง ให้ติดตามเครดิตคงเหลือในหน้า Billing แทน และทดสอบอีเมลอีกครั้งถ้าอัปเกรดเป็น paid plan
