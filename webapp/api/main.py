"""F5-01: เว็บแอป (FastAPI) เสิร์ฟหน้า prototype 4 หน้า + API รายชื่อหุ้น (ADR-0008).

    uvicorn webapp.api.main:app --reload        # แล้วเปิด http://127.0.0.1:8000

| route              | หน้า            |
|--------------------|-----------------|
| /                  | Home (Watchlist)|
| /search            | Search          |
| /stock/{ticker}    | Stock Detail    |
| /ask               | Ask AI          |
| /api/tickers       | รายชื่อหุ้นจาก config/tickers.yaml |
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parents[1] / "static"
TICKERS_FILE = ROOT / "config" / "tickers.yaml"

app = FastAPI(title="Stock News Sentiment", docs_url="/api/docs", redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@lru_cache
def load_tickers(path: Path = TICKERS_FILE) -> tuple[dict, ...]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    rows = tuple(
        {
            "ticker": t["ticker"],
            "name": t.get("name", ""),
            "sector": t.get("sector", ""),
        }
        for t in data.get("tickers", [])
    )
    if not rows:
        raise ValueError(f"no tickers in {path}")
    return rows


def known_ticker(ticker: str) -> str:
    symbol = ticker.upper()
    if symbol not in {t["ticker"] for t in load_tickers()}:
        raise HTTPException(status_code=404, detail=f"ticker {symbol} ไม่อยู่ในระบบ")
    return symbol


def _page(name: str) -> FileResponse:
    return FileResponse(STATIC / name, media_type="text/html")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return _page("index.html")


@app.get("/search", include_in_schema=False)
def search() -> FileResponse:
    return _page("search.html")


@app.get("/stock/{ticker}", include_in_schema=False)
def stock(ticker: str) -> FileResponse:
    return _page("stock.html")


@app.get("/ask", include_in_schema=False)
def ask() -> FileResponse:
    return _page("ask.html")


@app.get("/api/tickers")
def tickers() -> list[dict]:
    return list(load_tickers())
