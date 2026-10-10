"""โหลดรายชื่อ ticker จาก `config/tickers.yaml`."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

DEFAULT_TICKERS_PATH = Path(__file__).resolve().parents[2] / "config" / "tickers.yaml"
_TICKER_RE = re.compile(r"^[A-Z][A-Z.\-]{0,9}$")


def load_tickers(path: Path = DEFAULT_TICKERS_PATH) -> list[str]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = data.get("tickers") or []

    tickers: list[str] = []
    for entry in entries:
        symbol = entry["ticker"] if isinstance(entry, dict) else entry
        if not isinstance(symbol, str) or not _TICKER_RE.match(symbol):
            raise ValueError(f"invalid ticker in {path}: {symbol!r} (ต้องเป็นตัวพิมพ์ใหญ่)")
        if symbol in tickers:
            raise ValueError(f"duplicate ticker in {path}: {symbol}")
        tickers.append(symbol)

    if not tickers:
        raise ValueError(f"no tickers in {path}")
    return tickers
