"""F5-02: query Athena (workgroup `stock-sentiment`) สำหรับหน้า Stock Detail.

ใช้ credential เดียวกับ AWS CLI (~/.aws, profile จาก AWS_PROFILE) ไม่ต่อ S3 ตรง
ตั้งค่าผ่าน environment:
    ATHENA_WORKGROUP   (stock-sentiment)
    ATHENA_DATABASE    (stock_sentiment)
    AWS_REGION         (ap-southeast-2)
    MODEL_VERSION      (finbert-v1)  เวอร์ชันของ news_sentiment ที่แสดงบนเว็บ
"""

from __future__ import annotations

import os
import re
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

SAFE_VALUE = re.compile(r"^[A-Za-z0-9._\-]{1,40}$")
NY = "America/New_York"


@dataclass(frozen=True)
class AthenaConfig:
    workgroup: str = os.environ.get("ATHENA_WORKGROUP", "stock-sentiment")
    database: str = os.environ.get("ATHENA_DATABASE", "stock_sentiment")
    region: str = os.environ.get("AWS_REGION", "ap-southeast-2")
    model_version: str = os.environ.get("MODEL_VERSION", "finbert-v1")
    timeout_seconds: float = 30.0


class AthenaError(RuntimeError):
    pass


def _safe(value: str) -> str:
    """ค่าที่ใส่ลงใน SQL ต้องเป็นตัวอักษร/ตัวเลขธรรมดาเท่านั้น (กัน SQL injection)."""
    if not SAFE_VALUE.match(value):
        raise ValueError(f"unsafe value for SQL: {value!r}")
    return value


def daily_sql(db: str, ticker: str, version: str, days: int) -> str:
    """sentiment รายวัน (วันตามเวลานิวยอร์ก เหมือน trade_date) คู่กับราคาปิด."""
    t, v = _safe(ticker), _safe(version)
    lookback = int(days * 1.6) + 7  # วันปฏิทินพอให้ได้ `days` วันทำการ
    return f"""
WITH s AS (
  SELECT CAST(published_at AT TIME ZONE '{NY}' AS date) AS d, sentiment, sentiment_score
  FROM {db}.news_sentiment
  WHERE ticker = '{t}' AND model_version = '{v}'
    AND published_at >= current_timestamp - INTERVAL '{lookback}' DAY
), agg AS (
  SELECT d, count(*) AS news,
         count_if(sentiment = 'positive') AS positive,
         count_if(sentiment = 'neutral') AS neutral,
         count_if(sentiment = 'negative') AS negative,
         avg(sentiment_score) AS avg_score
  FROM s GROUP BY d
)
SELECT p.trade_date AS date, p.close,
       coalesce(a.news, 0) AS news, coalesce(a.positive, 0) AS positive,
       coalesce(a.neutral, 0) AS neutral, coalesce(a.negative, 0) AS negative,
       a.avg_score
FROM {db}.daily_price p
LEFT JOIN agg a ON a.d = p.trade_date
WHERE p.ticker = '{t}' AND p.trade_date >= current_date - INTERVAL '{lookback}' DAY
ORDER BY p.trade_date DESC
LIMIT {int(days)}
""".strip()


def news_sql(db: str, ticker: str, version: str, limit: int) -> str:
    t, v = _safe(ticker), _safe(version)
    return f"""
SELECT c.headline, c.source, c.url, c.published_at, ns.sentiment,
       ns.sentiment_score AS score
FROM {db}.news_sentiment ns
JOIN {db}.clean_news c ON c.news_id = ns.news_id AND c.ticker = ns.ticker
WHERE ns.ticker = '{t}' AND ns.model_version = '{v}'
  AND ns.published_at >= current_timestamp - INTERVAL '14' DAY
ORDER BY ns.published_at DESC
LIMIT {int(limit)}
""".strip()


def today_sql(db: str, ticker: str, version: str) -> str:
    t, v = _safe(ticker), _safe(version)
    return f"""
SELECT count(*) AS news,
       count_if(sentiment = 'positive') AS positive,
       count_if(sentiment = 'neutral') AS neutral,
       count_if(sentiment = 'negative') AS negative,
       max(processed_at) AS updated_at
FROM {db}.news_sentiment
WHERE ticker = '{t}' AND model_version = '{v}'
  AND published_at >= current_timestamp - INTERVAL '24' HOUR
""".strip()


def _convert(value: str | None, kind: str) -> Any:
    if value is None:
        return None
    if kind in ("integer", "bigint", "smallint", "tinyint"):
        return int(value)
    if kind in ("double", "float", "real", "decimal"):
        return float(value)
    if kind == "date":
        return date.fromisoformat(value).isoformat()
    if kind.startswith("timestamp"):
        ts = datetime.fromisoformat(value.replace(" ", "T")[:26])
        return ts.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return value


def parse_rows(pages: list[dict]) -> list[dict]:
    """แปลงผล get_query_results (หลายหน้า) เป็น list ของ dict ตามชนิดคอลัมน์."""
    if not pages:
        return []
    meta = pages[0]["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
    names = [c["Name"] for c in meta]
    kinds = [c["Type"].lower() for c in meta]
    out = []
    for i, page in enumerate(pages):
        rows = page["ResultSet"]["Rows"]
        for row in rows[1:] if i == 0 else rows:  # แถวแรกของหน้าแรกคือหัวตาราง
            values = [d.get("VarCharValue") for d in row["Data"]]
            out.append(
                {
                    n: _convert(v, k)
                    for n, v, k in zip(names, values, kinds, strict=True)
                }
            )
    return out


class AthenaClient:
    def __init__(self, config: AthenaConfig | None = None, client: Any = None) -> None:
        self.config = config or AthenaConfig()
        if client is None:
            import boto3

            client = boto3.client("athena", region_name=self.config.region)
        self._client = client

    def query(self, sql: str) -> list[dict]:
        c = self._client
        qid = c.start_query_execution(
            QueryString=sql,
            WorkGroup=self.config.workgroup,
            QueryExecutionContext={"Database": self.config.database},
        )["QueryExecutionId"]
        deadline = time.monotonic() + self.config.timeout_seconds
        wait = 0.2
        while True:
            status = c.get_query_execution(QueryExecutionId=qid)["QueryExecution"][
                "Status"
            ]
            state = status["State"]
            if state == "SUCCEEDED":
                break
            if state in ("FAILED", "CANCELLED"):
                raise AthenaError(status.get("StateChangeReason", state))
            if time.monotonic() > deadline:
                c.stop_query_execution(QueryExecutionId=qid)
                raise AthenaError(
                    f"query timed out after {self.config.timeout_seconds}s"
                )
            time.sleep(wait)
            wait = min(wait * 1.5, 1.0)
        pages = c.get_paginator("get_query_results").paginate(QueryExecutionId=qid)
        return parse_rows(list(pages))


def stock_detail(
    ticker: str,
    run: Callable[[str], list[dict]],
    config: AthenaConfig,
    days: int = 30,
    news_limit: int = 12,
) -> dict:
    """รวมผล 3 query เป็นรูปแบบเดียวกับ static/mock/stocks.json (รันพร้อมกัน)."""
    db, v = config.database, config.model_version
    with ThreadPoolExecutor(max_workers=3) as pool:
        daily_f = pool.submit(run, daily_sql(db, ticker, v, days))
        news_f = pool.submit(run, news_sql(db, ticker, v, news_limit))
        today_f = pool.submit(run, today_sql(db, ticker, v))
        daily = list(reversed(daily_f.result()))
        news = news_f.result()
        today = (today_f.result() or [{}])[0]

    for d in daily:
        if d.get("avg_score") is not None:
            d["avg_score"] = round(d["avg_score"], 3)
    for n in news:
        n["score"] = round(n["score"] or 0.0, 3)
        n["source"] = (n.get("source") or "").removeprefix("rss:").title()
    last = daily[-1] if daily else {}
    prev = daily[-2] if len(daily) > 1 else {}
    return {
        "ticker": ticker,
        "close": last.get("close"),
        "prev_close": prev.get("close"),
        "trade_date": last.get("date"),
        "today": {
            k: today.get(k) or 0 for k in ("news", "positive", "neutral", "negative")
        },
        "daily": daily,
        "news": news,
        "updated_at": today.get("updated_at"),
        "model_version": v,
    }
