# ADR-0008: เว็บแอปใช้ FastAPI + หน้าเว็บ HTML/JavaScript ล้วน และกราฟด้วย Chart.js

**Status:** Accepted

## Context
F5 ต้องมี 4 หน้า (Search, Home, Stock Detail, Ask AI) ที่ responsive และดึงข้อมูลจาก Athena (F5-02, F4-02) ทีม 2 คนเขียน Python เป็นหลัก ไม่มีใครถนัด framework frontend และเวลาในเทอม 1 มีน้อย

## Options
| ทางเลือก | ข้อดี | ข้อเสีย |
|---|---|---|
| React / Next.js + API แยก | component ใช้ซ้ำง่าย, ecosystem ใหญ่ | ต้องมี Node toolchain, build step, เรียนรู้ใหม่ |
| Streamlit | เร็วมากสำหรับ dashboard | ปรับ layout มือถือและเมนูล่างได้ยาก, ไม่เหมาะกับหลายหน้าแบบแอป |
| **FastAPI + HTML/JS ล้วน** | ภาษาเดียวกับ pipeline, ไม่มี build step, API และหน้าเว็บอยู่ใน process เดียว, ทดสอบด้วย pytest | เขียน DOM เอง, ถ้าหน้าเยอะขึ้นมากต้องจัดโค้ด JS ให้ดี |

## Decision
- **API:** FastAPI ใน `webapp/api/` เรียก Athena ผ่าน boto3 (workgroup `stock-sentiment`) ไม่ต่อ S3 ตรง
- **Frontend:** HTML + CSS + JavaScript ล้วนใน `webapp/static/` เสิร์ฟโดย FastAPI ตัวเดียวกัน ไม่มี build step
- **กราฟ:** Chart.js 4 จาก CDN (กราฟแท่ง sentiment + เส้นราคาปิด แกน y สองแกน)
- **หน้าตา:** ตามดีไซน์ของทีม (ภาพ User Flow ในเอกสารภาพรวมโครงงาน) พื้นขาว สะอาด สีหลักน้ำเงิน `#2563eb` การ์ดมุมมน โลโก้ตัวอักษรในกล่องสี่เหลี่ยม เมนูล่าง Home · Search · Ask AI
- **ชุดสี sentiment** (ใช้ทั้งระบบ คู่กับคำ Positive / Neutral / Negative เสมอ ไม่สื่อด้วยสีอย่างเดียว)

| ป้าย | สีตัวอักษร / จุด / แท่งกราฟ | พื้นหลังป้าย |
|---|---|---|
| Positive | `#16a34a` | `#dcfce7` |
| Neutral | `#64748b` | `#eef1f5` |
| Negative | `#dc2626` | `#fee2e2` |

## Consequences
- รันทั้งเว็บด้วยคำสั่งเดียว `uvicorn webapp.api.main:app`
- deploy เทอม 2 เป็น container เดียว (เช่น App Runner) ได้
- ถ้าหน้าซับซ้อนขึ้นมากในเทอม 2 ค่อยพิจารณา framework frontend ด้วย ADR ใหม่
