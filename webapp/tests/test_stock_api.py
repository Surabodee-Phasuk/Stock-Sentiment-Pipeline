import pytest

from webapp.api.athena import AthenaError
from webapp.tests.test_athena import CFG, fake_run

pytest.importorskip("fastapi")
pytest.importorskip("httpx")


@pytest.fixture
def api():
    from fastapi.testclient import TestClient

    from webapp.api import main

    class Fake:
        config = CFG
        calls = 0

        def query(self, sql):
            Fake.calls += 1
            return fake_run(sql)

    main._cache.clear()
    main.app.dependency_overrides[main.athena] = Fake
    yield TestClient(main.app), Fake
    main.app.dependency_overrides.clear()
    main._cache.clear()


def test_stock_api_returns_real_data_and_caches(api):
    client, fake = api
    res = client.get("/api/stock/nvda")

    assert res.status_code == 200
    body = res.json()
    assert body["ticker"] == "NVDA" and body["data_source"] == "Athena"
    assert len(body["daily"]) == 2 and body["news"][0]["sentiment"] == "positive"
    calls = fake.calls
    assert client.get("/api/stock/NVDA").status_code == 200
    assert fake.calls == calls  # ครั้งที่สองมาจาก cache


def test_stock_api_unknown_ticker_is_404(api):
    client, _ = api

    assert client.get("/api/stock/ZZZZ").status_code == 404


def test_stock_api_athena_error_is_503(api):
    from webapp.api import main

    class Broken:
        config = CFG

        def query(self, sql):
            raise AthenaError("no permission")

    main.app.dependency_overrides[main.athena] = Broken
    client, _ = api
    res = client.get("/api/stock/AAPL")

    assert res.status_code == 503 and "no permission" in res.json()["detail"]
