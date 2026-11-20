# `sentiment/`

FinBERT wrapper, gold set (`goldset/`) และสคริปต์ประเมิน (`eval/`)

**Owner:** M2  
**Issues:** F3-*

ดูกฎการทำงานที่ [docs/agents.md](../docs/agents.md)

| ไฟล์ | หน้าที่ |
|---|---|
| `finbert.py` | `FinBertClassifier`: โหลด `ProsusAI/finbert` (pretrained, ADR-0004) จำแนกเป็นชุด คืน `sentiment` + `score` |
| `pipeline.py` | ขั้นตอนร่วมของ streaming (F3-01) และ reprocess (F3-04): ตรวจ/ตัดซ้ำ → ตัดข่าวที่มีผลแล้ว → FinBERT → MERGE |

## ผลลัพธ์ที่เขียนลง `news_sentiment`
- `sentiment`: ป้ายที่ความน่าจะเป็นสูงสุด `positive` | `neutral` | `negative`
- `sentiment_score`: P(positive) − P(negative) ช่วง [−1, 1] ใช้เฉลี่ยรายวันได้ตรงๆ (ใกล้ 0 = กลางหรือไม่แน่ใจ)
- `model_name`, `model_version` (ค่าเริ่มต้น `ProsusAI/finbert`, `finbert-v1`)
- input = headline (+ summary ถ้ามี ตัดที่ 400 ตัวอักษร) ตัด token ที่ 128

## ลองในเครื่อง (ไม่ใช้ Spark)
```bash
.venv/bin/python -m pip install --group sentiment     # torch + transformers
.venv/bin/python -c "from sentiment.finbert import FinBertClassifier as F; print(F().predict(['Nvidia beats estimates']))"
```
