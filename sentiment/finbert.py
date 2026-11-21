"""F3-01: wrapper ของ FinBERT แบบ pretrained (ADR-0004) ใช้ร่วมกันใน streaming, reprocess และ eval.

    clf = FinBertClassifier()                 # โหลดโมเดลครั้งแรกตอนเรียก predict
    clf.predict(["Apple beats earnings estimates"])
    -> [Prediction(sentiment='positive', score=0.93, probs={...})]

- input: headline (+ summary ถ้ามี) ตาม docs/07
- `sentiment` = ป้ายที่ความน่าจะเป็นสูงสุด: positive | neutral | negative
- `score` = P(positive) - P(negative) อยู่ในช่วง [-1, 1] ใช้หาค่าเฉลี่ยรายวันได้ตรงๆ
  (บวก = ข่าวดี, ลบ = ข่าวร้าย, ใกล้ 0 = กลางหรือไม่แน่ใจ)
- ทุกผลลัพธ์บันทึก `model_name` และ `model_version` (เปลี่ยนโมเดลหรือวิธีสร้าง input
  = เพิ่ม version ใหม่ แล้ว reprocess จาก Raw ตาม F3-04)

torch / transformers import ตอนโหลดโมเดลเท่านั้น unit test จึงไม่ต้องลงไลบรารีเหล่านี้
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

MODEL_NAME = "ProsusAI/finbert"
MODEL_VERSION = "finbert-v1"
LABELS = ("positive", "neutral", "negative")
MAX_TOKENS = 128
MAX_SUMMARY_CHARS = 400


@dataclass(frozen=True)
class Prediction:
    sentiment: str
    score: float
    probs: Mapping[str, float] = field(default_factory=dict)


def build_text(headline: str | None, summary: str | None = None) -> str:
    """รวม headline กับ summary เป็น input เดียว ตัด summary ยาวเกินและช่องว่างซ้ำ."""
    head = " ".join((headline or "").split())
    body = " ".join((summary or "").split())[:MAX_SUMMARY_CHARS]
    if body and body.lower() != head.lower():
        if head and head[-1] not in ".!?":
            head += "."
        return f"{head} {body}".strip()
    return head


def to_prediction(probs: Mapping[str, float]) -> Prediction:
    """แปลงความน่าจะเป็นต่อป้ายเป็น Prediction (ป้ายต้องครบ 3 ค่าตาม LABELS)."""
    missing = set(LABELS) - set(probs)
    if missing:
        raise ValueError(f"missing labels from model output: {sorted(missing)}")
    clean = {label: float(probs[label]) for label in LABELS}
    sentiment = max(LABELS, key=lambda label: clean[label])
    score = round(clean["positive"] - clean["negative"], 6)
    return Prediction(sentiment=sentiment, score=score, probs=clean)


ProbFn = Callable[[Sequence[str]], list[dict[str, float]]]


class FinBertClassifier:
    """จำแนก sentiment เป็นชุด (batch) บน CPU หรือ GPU ถ้ามี.

    `prob_fn` ใช้แทนโมเดลจริงตอนทดสอบ: รับรายการข้อความ คืน dict ป้าย -> ความน่าจะเป็น
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        model_version: str = MODEL_VERSION,
        batch_size: int = 32,
        prob_fn: ProbFn | None = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        self.model_name = model_name
        self.model_version = model_version
        self.batch_size = batch_size
        self._prob_fn = prob_fn
        self.load_seconds = 0.0

    def _load(self) -> ProbFn:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        started = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        model.eval()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        id2label = {i: str(lbl).lower() for i, lbl in model.config.id2label.items()}

        def prob_fn(texts: Sequence[str]) -> list[dict[str, float]]:
            enc = tokenizer(
                list(texts),
                padding=True,
                truncation=True,
                max_length=MAX_TOKENS,
                return_tensors="pt",
            ).to(device)
            with torch.inference_mode():
                probs = torch.softmax(model(**enc).logits, dim=-1).cpu().tolist()
            return [{id2label[i]: p for i, p in enumerate(row)} for row in probs]

        self.load_seconds = time.perf_counter() - started
        return prob_fn

    def predict(self, texts: Sequence[str]) -> list[Prediction]:
        if not texts:
            return []
        if self._prob_fn is None:
            self._prob_fn = self._load()
        out: list[Prediction] = []
        for start in range(0, len(texts), self.batch_size):
            chunk = [
                t if t.strip() else "." for t in texts[start : start + self.batch_size]
            ]
            out.extend(to_prediction(p) for p in self._prob_fn(chunk))
        if len(out) != len(texts):
            raise RuntimeError(f"model returned {len(out)} results for {len(texts)}")
        return out
