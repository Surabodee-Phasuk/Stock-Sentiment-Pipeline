"""News event ตาม schema ใน docs/05-data-design.md (topic `stock-news`)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# query param ที่ใช้ติดตาม ไม่เปลี่ยนเนื้อหาข่าว ตัดทิ้งก่อน hash เพื่อให้ข่าวเดียวกันได้ news_id เดียวกัน
_TRACKING_PARAMS = {
    ".tsrc",
    "guccounter",
    "guce_referrer",
    "guce_referrer_sig",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ncid",
    "ref",
    "cmpid",
    "soc_src",
    "soc_trk",
}
_DEFAULT_PORTS = {"http": "80", "https": "443"}


def normalize_url(url: str) -> str:
    """ทำให้ URL ของข่าวเดียวกันเป็นสตริงเดียวกัน.

    - scheme/host เป็นตัวพิมพ์เล็ก, ตัด `www.`, ตัด default port
    - บังคับ https (ข่าวเดียวกันมักมีทั้ง http และ https)
    - ตัด fragment, ตัด tracking params (`utm_*` และรายการด้านบน), เรียง query
    - ตัด `/` ท้าย path
    """
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        raise ValueError(f"not an absolute URL: {url!r}")

    host = (parts.hostname or "").lower()
    host = host.removeprefix("www.")
    port = parts.port
    netloc = (
        host
        if port is None or str(port) == _DEFAULT_PORTS.get(parts.scheme.lower())
        else f"{host}:{port}"
    )

    query = sorted(
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.lower().startswith("utm_") and k.lower() not in _TRACKING_PARAMS
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(("https", netloc, path, urlencode(query), ""))


def make_news_id(url: str) -> str:
    """`news_id` = sha256 ของ URL ที่ normalize แล้ว (hex)."""
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()


def to_utc_iso(dt: datetime) -> str:
    """ISO 8601 UTC แบบ `2026-09-22T10:05:00Z` (ไม่มี microsecond)."""
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True, slots=True)
class NewsEvent:
    news_id: str
    ticker: str
    headline: str
    summary: str | None
    source: str
    url: str
    published_at: str
    ingested_at: str

    @classmethod
    def create(
        cls,
        *,
        ticker: str,
        headline: str,
        summary: str | None,
        source: str,
        url: str,
        published_at: datetime,
        ingested_at: datetime,
    ) -> NewsEvent:
        headline = " ".join(headline.split())
        if not headline:
            raise ValueError("headline is empty")
        summary = " ".join(summary.split()) if summary else None
        return cls(
            news_id=make_news_id(url),
            ticker=ticker.upper(),
            headline=headline,
            summary=summary or None,
            source=source,
            url=url.strip(),
            published_at=to_utc_iso(published_at),
            ingested_at=to_utc_iso(ingested_at),
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))
