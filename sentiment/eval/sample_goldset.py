"""F3-02: สุ่มข่าว 100 ชิ้นแบบกระจายตามหุ้น ไว้ให้คนติดป้าย (PoC ของ gold set, docs/07).

    # 1) เก็บข่าวหนึ่งรอบเป็น JSON Lines (ไม่ต้องมี Kafka)
    .venv/bin/python -m ingestion.news.collector --once --sink stdout > /tmp/news.jsonl
    # 2) สุ่ม 100 ข่าว → CSV ที่คอลัมน์ label ยังว่าง
    .venv/bin/python -m sentiment.eval.sample_goldset /tmp/news.jsonl \
        --out sentiment/goldset/poc_100.csv

ข่าวเดียวที่เกี่ยวกับหลายหุ้นถูกเลือกได้ครั้งเดียว (นับเป็นข่าวของหุ้นแรกที่สุ่มได้)
เก็บ headline + summary สั้นจาก RSS + url ไม่เก็บเนื้อข่าวเต็ม
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path

FIELDS = ("news_id", "ticker", "source", "published_at", "url", "headline", "summary")
GOLD_FIELDS = (*FIELDS, "label", "note")


def read_jsonl(paths: Iterable[Path]) -> list[dict]:
    rows = []
    for path in paths:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def stratified_sample(rows: Sequence[dict], n: int, seed: int = 42) -> list[dict]:
    """วนเลือกหุ้นละหนึ่งข่าวจนครบ n (หุ้นที่ข่าวน้อยหมดก่อน หุ้นอื่นเติมแทน)."""
    rng = random.Random(seed)
    by_ticker: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if r.get("news_id") and (r.get("headline") or "").strip():
            by_ticker[r["ticker"]].append(r)
    for items in by_ticker.values():
        rng.shuffle(items)

    picked: list[dict] = []
    seen: set[str] = set()
    tickers = sorted(by_ticker)
    while len(picked) < n and any(by_ticker.values()):
        for t in tickers:
            while by_ticker[t]:
                r = by_ticker[t].pop()
                if r["news_id"] not in seen:
                    seen.add(r["news_id"])
                    picked.append(r)
                    break
            if len(picked) == n:
                break
    return picked


def write_csv(rows: Sequence[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GOLD_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: " ".join(str(r.get(k) or "").split()) for k in FIELDS})


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="sample news for labelling")
    p.add_argument("jsonl", nargs="+", type=Path)
    p.add_argument("--out", type=Path, default=Path("sentiment/goldset/poc_100.csv"))
    p.add_argument("-n", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)

    rows = read_jsonl(args.jsonl)
    picked = stratified_sample(rows, args.n, args.seed)
    write_csv(picked, args.out)
    per = defaultdict(int)
    for r in picked:
        per[r["ticker"]] += 1
    print(
        f"read={len(rows)} picked={len(picked)} per_ticker={dict(sorted(per.items()))}"
    )
    print(f"wrote {args.out} — เติมคอลัมน์ label: positive | neutral | negative")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
