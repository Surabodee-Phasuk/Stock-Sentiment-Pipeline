# F3-02: PoC: F1 บน 100 ข่าว และ throughput

**Status:** done  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** FR-3.1  
**Branch:** `exp/f3-02-finbert-poc-benchmark`  
**PR:** [#34](https://github.com/Surabodee-Phasuk/Stock-Sentiment-Pipeline/pull/34)  

## งาน

- [x] ติดป้าย 100 ข่าว
- [x] วัด F1 และข่าว/วินาที

## Acceptance criteria

- รายงาน F1 และ throughput ใน Evidence

## File scope

`sentiment/eval/`

## Evidence

**ชุดข่าว:** `sentiment/goldset/poc_100.csv` = ข่าวจริงจาก collector หนึ่งรอบ (20 พ.ย. 2569, 304 ข่าว จาก Yahoo + Nasdaq RSS) สุ่มหุ้นละ 10 ข่าว รวม 100 ข่าว (`sample_goldset.py --seed 42`) M1 ติดป้ายเองหนึ่งคนตามเกณฑ์ใน `sentiment/goldset/README.md` โดยไม่ดูผล FinBERT ก่อน (positive 39, neutral 37, negative 24)

**F1 และ throughput** (`sentiment/eval/results/poc_100_finbert-v1.md`, ข่าวที่ทายผิดอยู่ใน `poc_100_finbert-v1_errors.csv`)

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

**สรุปผล**
- **Macro-F1 = 0.476 ต่ำกว่าเป้า 0.70** (เป้าของ O3 วัดบน gold set 300 ข่าวใน F3-03 แต่ผล PoC บอกแล้วว่า FinBERT แบบ pretrained ยังไม่แม่นพอสำหรับข่าวชุดนี้)
- จุดอ่อนหลักคือ **neutral** (F1 0.366): ข่าวที่คนมองว่าเป็นบวก ถูกทายเป็น neutral 16 จาก 39 ข่าว และข่าวที่คนมองว่าเป็นกลาง ถูกทายเป็นบวกหรือลบ 24 จาก 37 ข่าว
- **negative** ทำได้ดีที่สุด (recall 0.625)
- ข้อสังเกตจากข่าวที่ทายผิด: FinBERT ตัดสินจากน้ำเสียงของข้อความ ไม่ได้ตัดสินจากผลต่อหุ้นตัวที่อยู่ในแถว เช่น ข่าว Cisco หุ้นตกอยู่ใน feed ของ AVGO ถูกทายเป็น negative ทั้งที่คนมองว่าไม่เกี่ยวกับ AVGO โดยตรง
- ข้อจำกัด: ติดป้ายคนเดียว ยังไม่ได้วัดความเห็นตรงกันระหว่างคน (Cohen's kappa) ซึ่งเป็นงาน F3-03
- **Throughput ไม่เป็นคอขวด:** ข่าวประมาณ 311 ข่าวต่อรอบดึง (ทุก 10 นาที) ใช้เวลาจำแนกประมาณ 11 วินาทีบน CPU

**แนวทางต่อ (F3-03, เทอม 2):** gold set 300 ข่าวติดป้ายสองคน + kappa, ทดลองใช้ headline อย่างเดียวเทียบกับ headline + summary, และทดลองโมเดลอื่นผ่าน reprocess (F3-04) ด้วย `model_version` ใหม่ โดยไม่ต้องดึงข่าวใหม่

## Comments

- 2026-11-20 (M2): เพิ่ม `sentiment/eval/sample_goldset.py`, `sentiment/eval/evaluate.py` และชุด 100 ข่าว `sentiment/goldset/poc_100.csv` (ยังไม่มีป้าย) วัด throughput แล้ว 19.2 ข่าว/วินาที รอคนติดป้ายเพื่อวัด F1
- 2026-11-22 (M1): ติดป้ายครบ 100 ข่าวแล้ววัดผล Macro-F1 0.476, throughput 29.1 ข่าว/วินาที (ตัวเลข 19.2 ข่าว/วินาทีของวันที่ 20 พ.ย. เป็นการวัดรอบก่อนติดป้าย ใช้ผลรอบนี้แทน)
