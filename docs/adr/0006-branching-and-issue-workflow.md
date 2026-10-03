# ADR-0006: Trunk-based + 1 issue = 1 branch = 1 PR พร้อมชื่อ branch กำหนดล่วงหน้า

**Status:** Accepted

## Context
ทีม 2 คนและมี AI agent ช่วยเขียนโค้ด ต้องป้องกันการสร้าง branch มั่ว และให้ทุก PR ตามรอยกลับไปที่ requirement ได้

## Decision
- `main` protected, squash merge ผ่าน PR เท่านั้น, ไม่มี `develop`
- ชื่อ branch `<type>/<issue-id>-<slug>` ถูกเขียนไว้ใน issue ตั้งแต่ตอนวางโครงสร้างโปรเจกต์
- issue เก็บเป็น markdown ใน `docs/issues/` (ไม่ใช้ tracker ภายนอก)

## Consequences
- ทุกงานต้องมี issue ก่อน งานใหม่ต้องเพิ่ม issue ก่อนเริ่ม
- รายละเอียดอยู่ใน [docs/agents.md](../agents.md)
