// F5-01 / F5-02: หน้า Stock Detail — Overall Sentiment, Latest Price, ข่าวล่าสุด
// และกราฟ sentiment รายวันเทียบราคาปิด (FR-4.3)
"use strict";

SS.nav("");
const ticker = decodeURIComponent(location.pathname.split("/").pop()).toUpperCase();
const main = document.getElementById("main");
document.getElementById("title").textContent = ticker;

// แหล่งข้อมูลของหน้า: prototype ใช้ข้อมูลตัวอย่าง (F5-02 เปลี่ยนเป็น API จริง)
async function loadStock(t) {
  const data = await SS.mock();
  if (!data.stocks[t]) {
    const err = new Error("not found");
    err.status = 404;
    throw err;
  }
  return { ...data.stocks[t], data_source: "Sample data" };
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
      aria-label="Positive ${p}% Neutral ${n}% Negative ${100 - p - n}%">
      <span>${total ? shown + "%" : "–"}<small>${label}</small></span></div>`;
}

function chart(daily) {
  const css = getComputedStyle(document.documentElement);
  const color = (v) => css.getPropertyValue(v).trim();
  const scoreColor = (s) => (s > 0.05 ? color("--pos") : s < -0.05 ? color("--neg") : "#cbd5e1");
  Chart.defaults.font.family = color("--font");
  new Chart(document.getElementById("chart"), {
    data: {
      labels: daily.map((d) => SS.fmtDate(d.date).replace(/ \d{4}$/, "")),
      datasets: [
        {
          type: "bar",
          label: "Daily sentiment",
          data: daily.map((d) => d.avg_score),
          backgroundColor: daily.map((d) => scoreColor(d.avg_score)),
          borderRadius: 3,
          yAxisID: "y",
        },
        {
          type: "line",
          label: "Close (USD)",
          data: daily.map((d) => d.close),
          borderColor: color("--brand"),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
          yAxisID: "y1",
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "bottom", labels: { boxWidth: 10, color: color("--muted") } },
        tooltip: {
          callbacks: {
            afterBody: (items) => {
              const d = daily[items[0].dataIndex];
              return d.news ? `${d.news} news · +${d.positive} / ${d.neutral} / −${d.negative}` : "no news";
            },
          },
        },
      },
      scales: {
        y: { min: -1, max: 1, grid: { color: "#eef1f5" }, ticks: { color: color("--faint"), stepSize: 0.5 } },
        y1: { position: "right", grid: { display: false }, ticks: { color: color("--faint") } },
        x: { grid: { display: false }, ticks: { color: color("--faint"), maxRotation: 0, autoSkip: true, maxTicksLimit: 8 } },
      },
    },
  });
}

function watchStar() {
  const b = document.getElementById("star");
  const sync = () => {
    const on = SS.getWatchlist().includes(ticker);
    b.textContent = on ? "★" : "☆";
    b.classList.toggle("on", on);
    b.setAttribute("aria-label", on ? "เอาออกจาก Watchlist" : "เพิ่มเข้า Watchlist");
  };
  b.onclick = () => { SS.toggleWatch(ticker); sync(); };
  sync();
}

function render(s, info) {
  const c = s.today;
  const label = SS.dominant(c);
  const total = c.positive + c.neutral + c.negative;
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
        <p class="card-title">Overall Sentiment</p>
        ${
          c.news
            ? `<div class="row" style="flex-wrap:wrap;gap:16px">
                <span class="big-pill ${label}">${SS.LABEL_EN[label]}</span>
                ${donut(c)}
                <ul class="legend">${SS.LABELS.map(
                  (l) => `<li><span class="dot ${l}"></span>${SS.LABEL_EN[l]} ${SS.pct(c[l], total)}%</li>`
                ).join("")}</ul>
              </div>
              <p class="small faint" style="margin:12px 0 0">${c.news} news in the last 24 h · updated ${SS.fmtDateTime(s.updated_at)}</p>`
            : `<p class="empty" style="padding:12px 0">No news for ${s.ticker} in the last 24 hours</p>`
        }
      </div>
      <div class="card">
        <p class="card-title" style="margin-bottom:2px">Latest Price</p>
        <div class="small faint">as of ${SS.fmtDate(s.trade_date)}</div>
        <div class="price-big" style="margin:6px 0 2px">$${SS.fmtPrice(s.close)}</div>
        <div class="small" style="font-weight:600">${SS.change(s.close, s.prev_close)} <span class="faint" style="font-weight:400">Today</span></div>
        <div class="small faint" style="margin-top:8px">Daily close · not real-time</div>
      </div>
    </section>
    <section class="card">
      <div class="row" style="justify-content:space-between;margin-bottom:4px">
        <p class="card-title" style="margin:0">Latest News</p>
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
                    <a class="head" href="${SS.esc(n.url)}" target="_blank" rel="noopener">${SS.esc(n.headline)}</a>
                    <div class="small faint">${SS.esc(n.source)} · score ${n.score > 0 ? "+" : ""}${n.score.toFixed(2)}</div>
                  </div>
                  ${SS.pill(n.sentiment)}
                </li>`
              )
              .join("")}</ul>`
          : `<div class="empty">No news</div>`
      }
    </section>
    <section class="card">
      <p class="card-title">Sentiment vs Close · last ${s.daily.length} trading days</p>
      <div class="chart-box"><canvas id="chart" aria-label="Daily sentiment vs closing price"></canvas></div>
    </section>
    <section class="card">
      <p class="card-title" style="margin-bottom:4px">AI Summary</p>
      <p class="small faint" style="margin:0">สรุปข่าว 3–5 ประโยคด้วย LLM จะเปิดใช้ในเทอม 2 (F6)</p>
    </section>
    <p class="disclaimer">${SS.DISCLAIMER} · ป้ายและ score มาจาก FinBERT อาจผิดได้</p>`;
  if (s.daily.length && window.Chart) chart(s.daily);
  watchStar();
}

Promise.all([loadStock(ticker), SS.tickers()])
  .then(([s, list]) => render(s, list.find((t) => t.ticker === ticker)))
  .catch((e) => {
    main.innerHTML =
      e.status === 404
        ? `<div class="card empty">${SS.esc(ticker)} is not in the system<br><br><a class="btn" href="/search">Search stocks</a></div>`
        : `<div class="card empty">โหลดข้อมูลไม่สำเร็จ (${SS.esc(e.message)})<br><br><button onclick="location.reload()">ลองใหม่</button></div>`;
  });
