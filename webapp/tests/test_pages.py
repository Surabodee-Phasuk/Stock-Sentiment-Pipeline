import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from webapp.api.main import STATIC, app, load_tickers

client = TestClient(app)


@pytest.mark.parametrize("path", ["/", "/search", "/stock/NVDA", "/ask"])
def test_four_prototype_pages_render(path):
    res = client.get(path)

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/html")
    assert "/static/js/common.js" in res.text


def test_tickers_api_lists_config_tickers():
    res = client.get("/api/tickers")

    assert res.status_code == 200
    tickers = [t["ticker"] for t in res.json()]
    assert tickers == [t["ticker"] for t in load_tickers()]
    assert {"AAPL", "NVDA", "RKLB"} <= set(tickers)
    assert all(t["name"] and t["sector"] for t in res.json())


def test_every_page_shows_not_investment_advice():
    """FR-4.5 / docs/11: ทุกหน้าที่แสดง sentiment หรือคำตอบ AI ต้องมีข้อความนี้."""
    common = (STATIC / "js" / "common.js").read_text("utf-8")
    assert "ไม่ใช่คำแนะนำการลงทุน" in common
    for page in ["index.html", "stock.html", "ask.html"]:
        text = (STATIC / page).read_text("utf-8")
        js = (
            (STATIC / "js" / "stock.js").read_text("utf-8")
            if page == "stock.html"
            else ""
        )
        assert "DISCLAIMER" in text + js or "ไม่ใช่คำแนะนำการลงทุน" in text


def test_mock_data_covers_all_tickers_with_valid_labels():
    data = json.loads(Path(STATIC / "mock" / "stocks.json").read_text("utf-8"))
    tickers = {t["ticker"] for t in load_tickers()}

    assert set(data["stocks"]) == tickers
    for s in data["stocks"].values():
        assert {n["sentiment"] for n in s["news"]} <= {
            "positive",
            "neutral",
            "negative",
        }
        assert all(-1 <= d["avg_score"] <= 1 for d in s["daily"])
