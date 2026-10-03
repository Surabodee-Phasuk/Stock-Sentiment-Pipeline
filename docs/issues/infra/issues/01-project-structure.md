# INFRA-01: โครงสร้าง repo, เอกสาร, ชื่อ branch และ workflow

**Status:** in-review  
**Owner:** M1+M2  
**Phase:** PoC (T1/2569)  
**Refs:** NFR-6, ADR-0006  
**Branch:** `chore/infra-01-project-structure`  
**PR:** —

## งาน

- [x] โครงสร้างโฟลเดอร์ตาม docs/06 พร้อม README ทุกโฟลเดอร์
- [x] docs/ ตามรูปแบบ 00–11 + ADR + issues + BOARD
- [x] agents.md กำหนดชื่อ branch / commit / PR
- [x] PR template + issue template
- [x] `.gitignore` ครอบคลุม `.env`

## Acceptance criteria

- ทุก issue ใน BOARD มีชื่อ branch ที่ไม่ซ้ำกัน
- สมาชิกทั้งสองคนรีวิวและตกลง agents.md

## File scope

`docs/`, `.github/`, README ของทุกโฟลเดอร์

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
- 2026-10-03 (Claude, ขอโดย M1): วางโครงสร้างนี้ก่อนที่กฎ branch จะมีผล จึงทำบน branch ของ session `claude/wizardly-brahmagupta-lgsdtm` แทน `chore/infra-01-project-structure` — เป็นข้อยกเว้นครั้งเดียว งานต่อจากนี้ใช้ชื่อตาม BOARD
