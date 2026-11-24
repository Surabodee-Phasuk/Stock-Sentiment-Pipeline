# F5-05: หน้า Stock Detail เต็ม + disclaimer

**Status:** todo  
**Owner:** M2  
**Phase:** Full (T2/2570)  
**Refs:** FR-4.3, FR-4.5  
**Branch:** `feat/f5-05-stock-detail-full`  
**PR:** —

## งาน

- [ ] กราฟ sentiment รายวันเทียบราคาปิด 30 วันทำการ (Chart.js ตาม ADR-0008, ตามแบบใน Figma)
- [ ] ครบทุก state ใน docs/11
- [ ] ข้อความไม่ใช่คำแนะนำการลงทุน

## Acceptance criteria

- ข่าวใหม่แสดงภายใน 15 นาที

## File scope

`webapp/`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments

- 2026-11-23 (M1): ย้ายงานกราฟ sentiment เทียบราคาปิดจาก F5-02 มาที่นี่ เทอม 1 ออกแบบใน Figma ไว้ก่อน
