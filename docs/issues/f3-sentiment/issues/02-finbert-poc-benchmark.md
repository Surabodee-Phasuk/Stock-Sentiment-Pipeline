# F3-02: PoC: F1 บน 100 ข่าว และ throughput

**Status:** in-review  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-3.1  
**Branch:** `exp/f3-02-finbert-poc-benchmark`  
**PR:** —

## งาน

- [x] ติดป้าย 100 ข่าว
- [x] วัด F1 และข่าว/วินาที

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

**F1 และ throughput (ติดป้ายแล้ว 100 ข่าว):**

- model: `ProsusAI/finbert` (`finbert-v1`)
- news: 100 (input = headline + summary)
- machine: Darwin arm64 python 3.13.9
- run at: 2026-11-22 06:04 UTC

| Accuracy | Macro-Precision | Macro-Recall | Macro-F1 |
|---|---|---|---|
| 0.470 | 0.470 | 0.488 | 0.476 |

| ป้าย | Precision | Recall | F1 | จำนวน (gold) |
|---|---|---|---|---|
| positive | 0.528 | 0.487 | 0.507 | 39 |
| neutral | 0.382 | 0.351 | 0.366 | 37 |
| negative | 0.500 | 0.625 | 0.556 | 24 |

Confusion matrix (แถว = gold, คอลัมน์ = FinBERT)

| gold \ pred | positive | neutral | negative |
|---|---|---|---|
| positive | 19 | 16 | 4 |
| neutral | 13 | 13 | 11 |
| negative | 4 | 5 | 15 |

**Throughput:** 29.1 ข่าว/วินาที (100 ข่าว, median 3.438 s จาก 3 รอบ, batch 32, โหลดโมเดล 5.7 s)


## Comments

- 2026-11-20 (M2): เพิ่ม `sentiment/eval/sample_goldset.py`, `sentiment/eval/evaluate.py` และชุด 100 ข่าว `sentiment/goldset/poc_100.csv` (ยังไม่มีป้าย) วัด throughput แล้ว 19.2 ข่าว/วินาที รอคนติดป้ายเพื่อวัด F1 โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน)
