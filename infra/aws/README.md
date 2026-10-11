# `infra/aws/` — AWS foundation (INFRA-02)

คู่มือนี้บันทึก resource ที่สร้างไว้แล้วผ่าน AWS Console วิธีตรวจ และวิธีเปลี่ยนไปใช้สิทธิ์น้อยที่สุด

| ไฟล์ | หน้าที่ |
|---|---|
| `policy-dev.json` | IAM policy แบบ least privilege สำหรับ user ที่ใช้พัฒนา (แทน FullAccess) |
| `check.sh` | ตรวจว่า credential ในเครื่องเข้าถึง S3 / Glue / Athena ได้ และรัน `SELECT 1` |

## Resource ที่มีอยู่

| Resource | ค่า |
|---|---|
| Region | `ap-southeast-2` (Sydney) |
| S3 bucket | `stock-sentiment-lakehouse-surabodee` |
| Glue database | `stock_sentiment` |
| Athena workgroup | `stock-sentiment` |
| IAM user | `surabodee-dev` (M1) |
| Budget | `Stock_Sentiment` $10/เดือน แจ้งเตือนทางอีเมล |

**ทำไมใช้ Sydney:** บัญชีใช้ AWS Free plan ซึ่งบังคับให้ใช้ region นี้ ทุก resource และทุก client (Spark, Athena, เว็บแอป) ต้องตั้ง region เป็น `ap-southeast-2` ให้ตรงกัน

### โครงสร้าง prefix ใน bucket (ข้อเสนอ)
ยังไม่ได้ล็อกไว้ใน [docs/05](../../docs/05-data-design.md) จะยืนยันใน F2-01 / F2-02

```
s3://stock-sentiment-lakehouse-surabodee/
├── warehouse/        # ข้อมูลและ metadata ของตาราง Iceberg
├── checkpoints/      # Spark Structured Streaming checkpoint
└── athena-results/   # ผลลัพธ์ query ของ workgroup stock-sentiment
```

`policy-dev.json` ให้สิทธิ์ทั้ง bucket จึงไม่ต้องแก้ policy เมื่อ prefix เปลี่ยน

## ตั้งค่าเครื่อง
```bash
aws configure            # ใส่ access key ของ IAM user ตัวเอง, region = ap-southeast-2
bash infra/aws/check.sh  # ต้องจบด้วย "all checks passed"
```
Credential อยู่ใน `~/.aws/` นอก repo **ห้าม** ใส่ key ในไฟล์ใดๆ ของ repo (`.env` และ `.aws/` ถูก gitignore ไว้แล้ว) ถ้า M2 ต้องใช้ ให้สร้าง IAM user แยกและ attach policy เดียวกัน อย่าแชร์ key

## เปลี่ยนจาก FullAccess เป็น least privilege
ตอนนี้ `surabodee-dev` ใช้ FullAccess อยู่ 3 ตัว ให้ทำตามลำดับนี้เพื่อไม่ให้สิทธิ์ขาดระหว่างเปลี่ยน คำสั่งในขั้นที่ 1–2 และ 4 ต้องรันด้วยบัญชีที่มีสิทธิ์ IAM (เช่น admin) **ไม่ใช่** `surabodee-dev`

1. **ใส่ account ID แล้วตรวจ policy**
   ```bash
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   sed "s/ACCOUNT_ID/$ACCOUNT_ID/g" infra/aws/policy-dev.json > /tmp/policy-dev.json
   aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY \
     --policy-document file:///tmp/policy-dev.json --region ap-southeast-2
   ```
   ไฟล์ใน repo เก็บ `ACCOUNT_ID` เป็น placeholder ไว้ ไม่ใส่เลขจริง
2. **สร้าง policy แล้ว attach เพิ่ม** (ยังไม่ต้องถอด FullAccess)
   ```bash
   aws iam create-policy --policy-name StockSentimentDev --policy-document file:///tmp/policy-dev.json
   aws iam attach-user-policy --user-name surabodee-dev \
     --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/StockSentimentDev
   ```
3. **ตรวจว่าผลลัพธ์ Athena อยู่ใน bucket ของโปรเจกต์:** `check.sh` จะพิมพ์ result location ของ workgroup ออกมา ถ้าไม่ได้อยู่ใต้ `s3://stock-sentiment-lakehouse-surabodee/` ให้แก้ workgroup ให้ชี้ไปที่ `athena-results/` ก่อน ไม่อย่างนั้นหลังถอด FullAccess แล้ว `SELECT 1` จะเขียนผลลัพธ์ไม่ได้
4. **ดูชื่อ FullAccess ที่ attach อยู่ แล้วถอดออก**
   ```bash
   aws iam list-attached-user-policies --user-name surabodee-dev
   aws iam detach-user-policy --user-name surabodee-dev --policy-arn <ARN ของ FullAccess แต่ละตัว>
   ```
5. **รัน `bash infra/aws/check.sh` อีกครั้งด้วย `surabodee-dev`** ต้องผ่านครบ ถ้าขั้นไหนได้ `AccessDenied` ให้เพิ่มเฉพาะ action นั้นใน `policy-dev.json` แล้วรัน `aws iam create-policy-version --set-as-default` ห้ามกลับไปใช้ FullAccess

**policy นี้ไม่ครอบคลุม:** การสร้าง/ลบ bucket, database, workgroup และ IAM รวมถึง budget งานพวกนี้ทำด้วยบัญชี admin ผ่าน Console นานๆ ครั้ง ถ้าวันหลังต้องใช้บริการใหม่ (เช่น EMR หรือ Bedrock) ให้เพิ่ม statement ใหม่พร้อมจำกัด resource

## ความปลอดภัยของบัญชี
- **MFA บัญชีหลัก (root):** Console → ชื่อบัญชีมุมขวาบน → Security credentials → Multi-factor authentication (MFA) → Assign MFA device
- **ทดสอบอีเมล budget:** แก้ budget `Stock_Sentiment` ให้ยอดงบต่ำมากชั่วคราว (เช่น $0.01) แล้วรออีเมลในรอบที่ AWS อัปเดตค่าใช้จ่าย (อาจใช้เวลาหลายชั่วโมง) ได้อีเมลแล้วต้องตั้งกลับเป็น $10
