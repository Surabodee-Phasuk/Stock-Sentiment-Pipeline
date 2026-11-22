# FinBERT PoC — poc_100

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
