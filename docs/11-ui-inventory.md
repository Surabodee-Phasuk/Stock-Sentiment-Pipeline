# 11 — UI Inventory

ทุกหน้าที่มีในเว็บแอป (อัปเดตลิงก์โค้ดเมื่อสร้างจริง) — ไม่มีแอปมือถือ แต่หน้าเว็บต้อง responsive

Bottom menu: **Home · Search · Ask AI**

| Route | หน้า | ข้อมูลที่แสดง | States | Issue |
|---|---|---|---|---|
| `/search` | Search | ticker, ชื่อบริษัท, กลุ่มอุตสาหกรรม; ปุ่มเพิ่มเข้า watchlist | empty query, no result | F5-03 |
| `/` | Home (Watchlist) | การ์ดต่อหุ้น: ticker/ชื่อ, ราคาปิด + % เปลี่ยน, sentiment badge, สัดส่วน P/N/N, ข่าวล่าสุด, เวลาอัปเดต | watchlist ว่าง (ชวนไปหน้า Search), loading, error | F5-04 |
| `/stock/:ticker` | Stock Detail | กราฟ sentiment รายวัน vs ราคาปิด, สัดส่วน sentiment, ข่าวล่าสุด (แหล่ง, เวลา, label, score), (เทอม 2) สรุป LLM | ไม่มีข่าววันนี้, ticker นอกระบบ, loading | F5-02, F5-05, F6-02 |
| `/ask` | Ask AI | ช่องถาม, คำตอบ + citation | ปฏิเสธนอกขอบเขต, loading, error | F7-02 |

## หลัก UX
- คำถามหลักของผู้ใช้: “ข่าวของหุ้นนี้ช่วงล่าสุดเป็นบวก กลาง หรือลบ?” ต้องตอบได้ในหน้าจอแรก
- ทุกหน้าที่แสดง sentiment หรือคำตอบ AI ต้องมีข้อความ "ไม่ใช่คำแนะนำการลงทุน"
- สี sentiment: positive / neutral / negative ใช้ชุดสีเดียวทั้งระบบ (กำหนดใน F5-01)
