// F5-01 / F5-02: หน้า Stock Detail — Overall Sentiment, Latest Price, ข่าวล่าสุด
// (กราฟ sentiment รายวันเทียบราคาปิดทำในเทอม 2: F5-05)
"use strict";

SS.nav("");
const ticker = decodeURIComponent(location.pathname.split("/").pop()).toUpperCase();
const main = document.getElementById("main");
document.getElementById("title").textContent = ticker;

// แหล่งข้อมูลของหน้า: API จริงจาก Athena (F5-02) — เติม ?mock=1 เพื่อดูข้อมูลตัวอย่าง
const useMock = new URLSearchParams(location.search).has("mock");

async function loadStock(t) {
  if (!useMock) {
    const s = await SS.getJSON(`/api/stock/${encodeURIComponent(t)}`);
    return { ...s, data_source: `Live · Athena ${s.query_seconds}s` };
  }
  const data = await SS.mock();
  if (!data.stocks[t]) {
    const err = new Error("not found");
    err.status = 404;
    throw err;
  }
  return { ...data.stocks[t], data_source: "ข้อมูลตัวอย่าง", price_is_sample: true };
}

function donut(c) {
  const total = c.positive + c.neutral + c.negative;
  const p = SS.pct(c.positive, total);
  const n = SS.pct(c.neutral, total);
  const label = SS.dominant(c);
  const css = getComputedStyle(document.documentElement);
  const v = (x) => css.getPropertyValue(x).trim();
  const bg = total
    ? `conic-gradient(${v("--pos")} 0 ${p}%, #cbd5e1 ${p}% ${p + n}%, ${v("--neg")} ${p + n}% 100%)`
    : "#e5e9f0";
  const shown = SS.pct(c[label], total);
  return `<div class="donut" style="background:${bg}" role="img"
      aria-label="เชิงบวก ${p}% เป็นกลาง ${n}% เชิงลบ ${100 - p - n}%">
      <span>${total ? shown + "%" : "–"}<small>${SS.LABEL_TH[label]}</small></span></div>`;
}

function watchStar() {
  const b = document.getElementById("star");
  const sync = () => {
    const on = SS.getWatchlist().includes(ticker);
    b.textContent = on ? "★" : "☆";
    b.classList.toggle("on", on);
    b.setAttribute("aria-label", on ? "เอาออกจากรายการติดตาม" : "เพิ่มเข้ารายการติดตาม");
  };
  b.onclick = () => { SS.toggleWatch(ticker); sync(); };
  sync();
}

function render(s, info) {
  const c = s.today;
  const label = SS.dominant(c);
  const total = c.positive + c.neutral + c.negative;
  // ราคาใน mock เป็นค่าสุ่ม ต้องมีป้ายกำกับเสมอ
  const sampleTag = s.price_is_sample ? `<span class="sample">ข้อมูลตัวอย่าง</span>` : "";
  document.title = `${s.ticker} · Stock News Sentiment`;
  document.getElementById("head").innerHTML = `
    <a class="back" href="/" aria-label="กลับ">←</a>
    ${SS.logo(s.ticker, true)}
    <div class="grow"><span class="ticker" style="font-size:18px">${s.ticker}</span>
      <span class="name" style="font-size:13px"> ${SS.esc(info?.name ?? "")}</span></div>
    ${c.news ? SS.pill(label) : ""}
    <button class="icon-btn" id="star" type="button"></button>`;
  main.innerHTML = `
    <section class="grid-2">
      <div class="card">
        <p class="card-title">ภาพรวมความรู้สึกของข่าว</p>
        ${
          c.news
            ? `<div class="row" style="flex-wrap:wrap;gap:16px">
                <span class="big-pill ${label}">${SS.LABEL_TH[label]}</span>
                ${donut(c)}
                <ul class="legend">${SS.LABELS.map(
                  (l) => `<li><span class="dot ${l}"></span>${SS.LABEL_TH[l]} ${SS.pct(c[l], total)}%</li>`
                ).join("")}</ul>
              </div>
              <p class="small faint" style="margin:12px 0 0">${c.news} ข่าวใน 24 ชั่วโมงล่าสุด · อัปเดต ${SS.fmtDateTime(s.updated_at)}</p>`
            : `<p class="empty" style="padding:12px 0">ไม่มีข่าวของ ${s.ticker} ใน 24 ชั่วโมงล่าสุด</p>`
        }
      </div>
      <div class="card">
        <div class="row" style="margin-bottom:2px">
          <p class="card-title" style="margin:0">ราคาปิดล่าสุด</p>${sampleTag}
        </div>
        <div class="small faint">ณ วันที่ ${SS.fmtDate(s.trade_date)}</div>
        <div class="price-big" style="margin:6px 0 2px">$${SS.fmtPrice(s.close)}</div>
        <div class="small" style="font-weight:600">${SS.change(s.close, s.prev_close)} <span class="faint" style="font-weight:400">เทียบวันก่อนหน้า</span></div>
        <div class="small faint" style="margin-top:8px">ราคาปิดรายวัน ไม่ใช่เวลาจริง</div>
      </div>
    </section>
    <section class="card">
      <div class="row" style="justify-content:space-between;margin-bottom:4px">
        <p class="card-title" style="margin:0">ข่าวล่าสุด</p>
        <span class="small faint">${SS.esc(s.data_source)}</span>
      </div>
      ${
        s.news.length
          ? `<ul class="list">${s.news
              .map(
                (n) => `<li class="news-item">
                  <span class="dot ${n.sentiment}"></span>
                  <time datetime="${SS.esc(n.published_at)}" title="${SS.fmtDateTime(n.published_at)}">${SS.fmtClock(n.published_at)}</time>
                  <div class="grow">
                    <a class="head" href="${SS.esc(n.url)}" target="_blank" rel="noopener">${SS.esc(SS.headline(n))}</a>
                    ${n.headline_th ? `<div class="small faint" lang="en">${SS.esc(n.headline)}</div>` : ""}
                    <div class="small faint">${SS.esc(n.source)} · คะแนน ${n.score > 0 ? "+" : ""}${n.score.toFixed(2)}</div>
                  </div>
                  ${SS.pill(n.sentiment)}
                </li>`
              )
              .join("")}</ul>`
          : `<div class="empty">ไม่มีข่าว</div>`
      }
    </section>
    <section class="card">
      <p class="card-title" style="margin-bottom:4px">สรุปข่าวโดย AI</p>
      <p class="small faint" style="margin:0">สรุปข่าว 3–5 ประโยคด้วย LLM จะเปิดใช้ในเทอม 2 (F6)</p>
    </section>
    <p class="disclaimer">${SS.DISCLAIMER} · ป้ายและคะแนนมาจาก FinBERT อาจผิดได้${s.news.some((n) => n.headline_th) ? " · หัวข้อข่าวภาษาไทยแปลด้วย AI อาจคลาดเคลื่อน โปรดดูต้นฉบับ" : ""}</p>`;
  watchStar();
}

Promise.all([loadStock(ticker), SS.tickers()])
  .then(([s, list]) => render(s, list.find((t) => t.ticker === ticker)))
  .catch((e) => {
    main.innerHTML =
      e.status === 404
        ? `<div class="card empty">${SS.esc(ticker)} ไม่อยู่ในระบบ<br><br><a class="btn" href="/search">ค้นหาหุ้น</a></div>`
        : `<div class="card empty">โหลดข้อมูลไม่สำเร็จ (${SS.esc(e.message)})<br><br><button onclick="location.reload()">ลองใหม่</button></div>`;
  });
