// F5-01: ส่วนร่วมของทุกหน้า — เมนูล่าง, watchlist, โลโก้, ป้าย sentiment, รูปแบบเวลา/ตัวเลข
"use strict";

const SS = (() => {
  const LABELS = ["positive", "neutral", "negative"];
  const LABEL_TH = { positive: "เชิงบวก", neutral: "เป็นกลาง", negative: "เชิงลบ" };
  const SECTOR_TH = {
    Technology: "เทคโนโลยี", "Communication Services": "บริการสื่อสาร",
    "Consumer Discretionary": "สินค้าฟุ่มเฟือย", Semiconductors: "เซมิคอนดักเตอร์",
    Automotive: "ยานยนต์", Aerospace: "อวกาศและการบิน",
  };
  const WATCH_KEY = "ss.watchlist";
  const DEFAULT_WATCH = ["RKLB", "NVDA", "TSLA"];
  // สีพื้นโลโก้ตัวอักษร (ไม่ใช่โลโก้จริงของบริษัท)
  const LOGO = {
    RKLB: "#111827", NVDA: "#65a30d", TSLA: "#dc2626", AAPL: "#4b5563", MSFT: "#0284c7",
    GOOGL: "#2563eb", AMZN: "#ea580c", META: "#1d4ed8", AVGO: "#b91c1c", SPCX: "#334155",
  };

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
    );

  const ICONS = {
    home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    ask: '<path d="M4 5h16v11H8l-4 4z"/><path d="M9 10h6"/>',
  };
  function nav(active) {
    const items = [["/", "หน้าแรก", "home"], ["/search", "ค้นหา", "search"], ["/ask", "ถาม AI", "ask"]];
    const el = document.createElement("nav");
    el.className = "bottom";
    el.setAttribute("aria-label", "เมนูหลัก");
    el.innerHTML = items
      .map(
        ([href, text, key]) =>
          `<a href="${href}"${key === active ? ' aria-current="page"' : ""}>` +
          `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ` +
          `stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[key]}</svg>${text}</a>`
      )
      .join("");
    document.body.appendChild(el);
  }

  function getWatchlist() {
    try {
      const v = JSON.parse(localStorage.getItem(WATCH_KEY));
      return Array.isArray(v) ? v : DEFAULT_WATCH.slice();
    } catch {
      return DEFAULT_WATCH.slice();
    }
  }
  function setWatchlist(list) {
    try {
      localStorage.setItem(WATCH_KEY, JSON.stringify([...new Set(list)]));
    } catch {
      /* private mode: ใช้ค่าในหน้านี้ต่อได้ */
    }
  }
  function toggleWatch(ticker) {
    const list = getWatchlist();
    const i = list.indexOf(ticker);
    if (i >= 0) list.splice(i, 1);
    else list.push(ticker);
    setWatchlist(list);
    return i < 0;
  }

  // ป้ายที่มีข่าวมากที่สุด เสมอกันให้ neutral
  function dominant(c) {
    const top = Math.max(c.positive, c.neutral, c.negative);
    if (!top) return "neutral";
    const winners = LABELS.filter((l) => c[l] === top);
    return winners.length === 1 ? winners[0] : "neutral";
  }
  const pct = (n, total) => (total ? Math.round((n / total) * 100) : 0);

  const pill = (label) => `<span class="pill ${label}">${LABEL_TH[label]}</span>`;
  const sector = (s) => SECTOR_TH[s] ?? s;
  // แสดงหัวข้อข่าวภาษาไทย ถ้ายังไม่มีคำแปลใช้ต้นฉบับ (ข่าวต้นทางและ FinBERT เป็นภาษาอังกฤษ)
  const headline = (n) => n.headline_th || n.headline;
  function logo(ticker, big) {
    const color = LOGO[ticker] || "#475569";
    return `<span class="logo${big ? " lg" : ""}" style="background:${color}" aria-hidden="true">${esc(
      ticker.slice(0, 2)
    )}</span>`;
  }

  const timeFmt = new Intl.DateTimeFormat("th-TH", {
    hour: "2-digit", minute: "2-digit", timeZone: "Asia/Bangkok",
  });
  const dateTimeFmt = new Intl.DateTimeFormat("th-TH", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Asia/Bangkok",
  });
  const dateFmt = new Intl.DateTimeFormat("th-TH", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  const fmtClock = (iso) => (iso ? timeFmt.format(new Date(iso)) : "—");
  const fmtDateTime = (iso) => (iso ? dateTimeFmt.format(new Date(iso)) : "—");
  const fmtDate = (d) => (d ? dateFmt.format(new Date(d + "T00:00:00Z")) : "—");
  const fmtPrice = (n) =>
    n == null ? "—" : n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function change(close, prev) {
    if (close == null || !prev) return "";
    const diff = close - prev;
    const p = (diff / prev) * 100;
    const sign = diff >= 0 ? "+" : "−";
    return `<span class="${diff >= 0 ? "up" : "down"}">${sign}${Math.abs(diff).toFixed(2)} (${sign}${Math.abs(p).toFixed(1)}%)</span>`;
  }

  async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) {
      const err = new Error(`HTTP ${res.status}`);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }
  let tickersCache;
  const tickers = () => (tickersCache ??= getJSON("/api/tickers"));
  let mockCache;
  const mock = () => (mockCache ??= getJSON("/static/mock/stocks.json"));

  const DISCLAIMER = "ข้อมูลนี้สรุปทิศทางความรู้สึกของข่าวเท่านั้น ไม่ใช่คำแนะนำการลงทุน";

  return {
    LABELS, LABEL_TH, sector, headline, esc, nav, getWatchlist, setWatchlist, toggleWatch, dominant, pct,
    pill, logo, fmtClock, fmtDateTime, fmtDate, fmtPrice, change, getJSON, tickers, mock,
    DISCLAIMER,
  };
})();
