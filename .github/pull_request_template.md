<!-- Title: [F1-01] Short summary — ชื่อ branch ต้องตรงกับ field Branch ใน issue -->

## Issue
- ID: <!-- เช่น F1-01 -->
- File: <!-- docs/issues/<feature>/issues/<NN>-<slug>.md -->
- Branch ตรงกับ issue: [ ]

## What changed
-

## Evidence
<!-- ผลทดสอบ, query + ผลลัพธ์, ภาพหน้าจอ, ตัวเลขที่วัดได้ -->

## Checklist
- [ ] sync `main` แล้ว
- [ ] `ruff check . && ruff format --check . && pytest` ผ่าน (ถ้ามีโค้ด Python)
- [ ] อัปเดตไฟล์ issue (checklist, Status, PR, Evidence)
- [ ] อัปเดตแถวใน `docs/issues/BOARD.md`
- [ ] แก้ `docs/05-data-design.md` ถ้าเปลี่ยน schema
- [ ] เพิ่ม ADR ถ้าเปลี่ยนการตัดสินใจที่ล็อกแล้ว
- [ ] ไม่มี secret / credential ใน diff
- [ ] แก้ไฟล์เฉพาะใน File scope (หรืออธิบายเหตุผล)
