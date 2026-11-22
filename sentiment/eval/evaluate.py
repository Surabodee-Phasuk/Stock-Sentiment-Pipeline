"""F3-02: วัด FinBERT กับข่าวที่ติดป้ายแล้ว — Accuracy, Precision / Recall / F1 ต่อป้าย,
Macro-F1 และ throughput (ข่าว/วินาที).

    .venv/bin/python -m pip install --group sentiment
    .venv/bin/python -m sentiment.eval.evaluate sentiment/goldset/poc_100.csv

ผลเขียนเป็น markdown + json ใน sentiment/eval/results/ (ใส่ Evidence และรายงานบทที่ 4)
ไม่ใช้ scikit-learn: สูตรอยู่ใน `confusion` / `metrics` ทดสอบด้วย unit test
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import time
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from sentiment.finbert import LABELS, MODEL_NAME, MODEL_VERSION, build_text

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def read_gold(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    bad = [
        (i + 2, r.get("label"))
        for i, r in enumerate(rows)
        if (r.get("label") or "").strip().lower() not in LABELS
    ]
    if bad:
        raise ValueError(f"rows without a valid label (line, value): {bad[:10]}")
    for r in rows:
        r["label"] = r["label"].strip().lower()
    return rows


def confusion(gold: Sequence[str], pred: Sequence[str]) -> dict[str, dict[str, int]]:
    """matrix[gold][pred]."""
    if len(gold) != len(pred):
        raise ValueError("gold and pred lengths differ")
    m = {g: dict.fromkeys(LABELS, 0) for g in LABELS}
    for g, p in zip(gold, pred, strict=True):
        m[g][p] += 1
    return m


def metrics(gold: Sequence[str], pred: Sequence[str]) -> dict:
    m = confusion(gold, pred)
    per = {}
    for c in LABELS:
        tp = m[c][c]
        fp = sum(m[g][c] for g in LABELS if g != c)
        fn = sum(m[c][p] for p in LABELS if p != c)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (
            2 * precision * recall / (precision + recall) if precision + recall else 0.0
        )
        per[c] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": tp + fn,
        }
    n = len(gold)
    return {
        "n": n,
        "accuracy": sum(m[c][c] for c in LABELS) / n if n else 0.0,
        "macro_precision": statistics.fmean(per[c]["precision"] for c in LABELS),
        "macro_recall": statistics.fmean(per[c]["recall"] for c in LABELS),
        "macro_f1": statistics.fmean(per[c]["f1"] for c in LABELS),
        "per_label": per,
        "confusion": m,
    }


def throughput(clf, texts: Sequence[str], repeats: int = 3) -> dict:
    clf.predict(texts[: min(8, len(texts))])  # warm-up (โหลดโมเดล)
    runs = []
    for _ in range(repeats):
        started = time.perf_counter()
        clf.predict(texts)
        runs.append(time.perf_counter() - started)
    best = statistics.median(runs)
    return {
        "texts": len(texts),
        "repeats": repeats,
        "median_seconds": round(best, 3),
        "news_per_second": round(len(texts) / best, 1) if best else 0.0,
        "batch_size": clf.batch_size,
        "load_seconds": round(clf.load_seconds, 1),
    }


def to_markdown(name: str, result: dict) -> str:
    m, t = result["metrics"], result["throughput"]
    lines = [
        f"# FinBERT PoC — {name}",
        "",
        f"- model: `{result['model_name']}` (`{result['model_version']}`)",
        f"- news: {m['n']} (input = headline + summary)",
        f"- machine: {result['machine']}",
        f"- run at: {result['run_at']}",
        "",
        "| Accuracy | Macro-Precision | Macro-Recall | Macro-F1 |",
        "|---|---|---|---|",
        (
            f"| {m['accuracy']:.3f} | {m['macro_precision']:.3f} "
            f"| {m['macro_recall']:.3f} | {m['macro_f1']:.3f} |"
        ),
        "",
        "| ป้าย | Precision | Recall | F1 | จำนวน (gold) |",
        "|---|---|---|---|---|",
    ]
    for c in LABELS:
        p = m["per_label"][c]
        lines.append(
            f"| {c} | {p['precision']:.3f} | {p['recall']:.3f} | {p['f1']:.3f} "
            f"| {p['support']} |"
        )
    lines += ["", "Confusion matrix (แถว = gold, คอลัมน์ = FinBERT)", ""]
    lines.append("| gold \\ pred | " + " | ".join(LABELS) + " |")
    lines.append("|---" * (len(LABELS) + 1) + "|")
    for g in LABELS:
        row = " | ".join(str(m["confusion"][g][p]) for p in LABELS)
        lines.append(f"| {g} | {row} |")
    lines += [
        "",
        (
            f"**Throughput:** {t['news_per_second']} ข่าว/วินาที "
            f"({t['texts']} ข่าว, median {t['median_seconds']} s "
            f"จาก {t['repeats']} รอบ, batch {t['batch_size']}, "
            f"โหลดโมเดล {t['load_seconds']} s)"
        ),
        "",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="evaluate FinBERT on labelled news")
    p.add_argument("gold", type=Path)
    p.add_argument("--model-name", default=MODEL_NAME)
    p.add_argument("--model-version", default=MODEL_VERSION)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--out-dir", type=Path, default=RESULTS_DIR)
    args = p.parse_args(argv)

    from sentiment.finbert import FinBertClassifier

    gold_rows = read_gold(args.gold)
    texts = [build_text(r["headline"], r.get("summary")) for r in gold_rows]
    clf = FinBertClassifier(args.model_name, args.model_version, args.batch_size)
    preds = clf.predict(texts)
    result = {
        "model_name": clf.model_name,
        "model_version": clf.model_version,
        "machine": f"{platform.system()} {platform.machine()} "
        f"python {platform.python_version()}",
        "run_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "metrics": metrics(
            [r["label"] for r in gold_rows], [x.sentiment for x in preds]
        ),
        "throughput": throughput(clf, texts),
    }

    name = args.gold.stem
    args.out_dir.mkdir(parents=True, exist_ok=True)
    md = to_markdown(name, result)
    (args.out_dir / f"{name}_{clf.model_version}.md").write_text(md, encoding="utf-8")
    (args.out_dir / f"{name}_{clf.model_version}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    mismatches = args.out_dir / f"{name}_{clf.model_version}_errors.csv"
    with mismatches.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["news_id", "ticker", "gold", "finbert", "score", "headline"])
        for r, x in zip(gold_rows, preds, strict=True):
            if r["label"] != x.sentiment:
                w.writerow(
                    [
                        r["news_id"],
                        r["ticker"],
                        r["label"],
                        x.sentiment,
                        x.score,
                        r["headline"],
                    ]
                )
    print(md)
    print(f"wrote {args.out_dir}/{name}_{clf.model_version}.(md|json) and errors csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
