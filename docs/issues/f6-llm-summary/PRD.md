# PRD: F6 — LLM Summary

สรุปข่าวประจำวันของแต่ละหุ้นพร้อมเหตุผลของ sentiment ใช้เฉพาะข่าวในชั้น Cleaned

**อ้างอิง:** FR-5.1–FR-5.2 ใน [docs/04-requirements.md](../../04-requirements.md)  
**Milestones:** M4, M6, M7

## Issues

| # | งาน | Owner | Phase | Branch |
|---|---|---|---|---|
| [01](issues/01-llm-summary-poc.md) | PoC: สรุป 5 ชิ้น ตรวจด้วยคน + ค่าใช้จ่ายต่อชิ้น + ADR เลือก LLM | M1+M2 | PoC (T1/2569) | `exp/f6-01-llm-summary-poc` |
| [02](issues/02-llm-summary-service.md) | สรุปรายวันอัตโนมัติ + cache + แสดงใน Stock Detail | M1+M2 | Full (T2/2570) | `feat/f6-02-llm-summary-service` |
| [03](issues/03-llm-summary-eval-50.md) | ประเมิน 50 สรุป | M1+M2 | Full (T2/2570) | `test/f6-03-llm-summary-eval-50` |
