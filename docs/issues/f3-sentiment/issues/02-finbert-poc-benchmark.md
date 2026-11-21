# F3-02: PoC: F1 บน 100 ข่าว และ throughput

**Status:** in-progress  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-3.1  
**Branch:** `exp/f3-02-finbert-poc-benchmark`  
**PR:** —

## งาน

- [ ] ติดป้าย 100 ข่าว
- [ ] วัด F1 และข่าว/วินาที

## Acceptance criteria

- รายงาน F1 และ throughput ใน Evidence

## File scope

`sentiment/eval/`

## Evidence

**ชุดข่าว:** `sentiment/goldset/poc_100.csv` = ข่าวจริงจาก collector หนึ่งรอบ (20 พ.ย. 2569, 304 ข่าว จาก Yahoo + Nasdaq RSS) สุ่มหุ้นละ 10 ข่าว รวม 100 ข่าว (`sample_goldset.py --seed 42`)

**Throughput** (FinBERT `ProsusAI/finbert` บน CPU, input = headline + summary, batch 32)
```
100 ข่าว, median 5.197 s จาก 3 รอบ → 19.2 ข่าว/วินาที (โหลดโมเดล 2.5 s)
เครื่อง: MacBook (Apple Silicon) CPU, Python 3.13, torch 2.x
```
- เทียบกับข่าวเข้าระบบ ~300 ข่าวต่อรอบ (ทุก 10 นาที) → ใช้เวลาจำแนก ~16 วินาทีต่อรอบ ไม่เป็นคอขวดของ latency 15 นาที

**F1:** _(รอติดป้าย 100 ข่าว แล้วรัน `python -m sentiment.eval.evaluate sentiment/goldset/poc_100.csv` ผลจะอยู่ใน `sentiment/eval/results/`)_

## Comments

- 2026-11-20 (M2): เพิ่ม `sentiment/eval/sample_goldset.py`, `sentiment/eval/evaluate.py` และชุด 100 ข่าว `sentiment/goldset/poc_100.csv` (ยังไม่มีป้าย) วัด throughput แล้ว 19.2 ข่าว/วินาที รอคนติดป้ายเพื่อวัด F1 โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
