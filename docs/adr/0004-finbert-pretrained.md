# ADR-0004: ใช้ FinBERT แบบ pretrained สำหรับ sentiment รายข่าว

**Status:** Accepted

## Decision
ใช้ FinBERT pretrained จำแนก positive / neutral / negative ไม่ fine-tune และไม่ฝึกโมเดลภาษาใหม่ บันทึก `model_version` ทุกผลลัพธ์

## Consequences
- วัดคุณภาพด้วย gold set 300 ข่าว เป้าหมาย Macro-F1 ≥ 0.70
- เปลี่ยนโมเดลได้โดย reprocess จาก Raw
