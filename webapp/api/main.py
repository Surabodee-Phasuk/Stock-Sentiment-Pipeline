"""F5-01: เว็บแอป (FastAPI) เสิร์ฟหน้า prototype 4 หน้า + API รายชื่อหุ้น (ADR-0008).

    uvicorn webapp.api.main:app --reload        # แล้วเปิด http://127.0.0.1:8000

| route              | หน้า            |
|--------------------|-----------------|
| /                  | Home (Watchlist)|
| /search            | Search          |
| /stock/{ticker}    | Stock Detail    |
| /ask               | Ask AI          |
| /api/tickers       | รายชื่อหุ้นจาก config/tickers.yaml |
| /api/stock/{ticker}| ข้อมูลจริงจาก Athena สำหรับ Stock Detail (F5-02) |
"""

from __future__ import annotations

import time
from functools import lru_cache
from pathlib import Path
from typing import Annotated

import yaml
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from webapp.api.athena import AthenaClient, AthenaConfig, AthenaError, stock_detail

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


CACHE_SECONDS = 300  # ข้อมูลอัปเดตทุก ~10 นาที cache 5 นาทีพอ และลดค่า query Athena
_cache: dict[tuple[str, int], tuple[float, dict]] = {}


@lru_cache
def athena() -> AthenaClient:
    return AthenaClient(AthenaConfig())


@app.get("/api/stock/{ticker}")
def stock_api(
    ticker: str,
    client: Annotated[AthenaClient, Depends(athena)],
    days: Annotated[int, Query(ge=5, le=90)] = 30,
) -> dict:
    symbol = known_ticker(ticker)
    key = (symbol, days)
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < CACHE_SECONDS:
        return hit[1]
    started = time.monotonic()
    try:
        data = stock_detail(symbol, client.query, client.config, days=days)
    except AthenaError as exc:
        raise HTTPException(status_code=503, detail=f"Athena: {exc}") from exc
    data["query_seconds"] = round(time.monotonic() - started, 2)
    data["data_source"] = "Athena"
    _cache[key] = (time.monotonic(), data)
    return data
