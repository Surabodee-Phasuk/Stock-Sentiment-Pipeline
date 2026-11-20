-- F2-04: query ข่าวคู่กับราคาปิดผ่าน Athena (acceptance criteria, FR-2.4)
-- รันใน Athena workgroup `stock-sentiment` ทีละ query ดู Run time ใน Query stats ด้วย (NFR-3: ≤ 5 วินาที)

-- 1) daily_price ต้องไม่มีแถวซ้ำต่อ (ticker, trade_date)
SELECT count(*) AS rows,
       count(DISTINCT concat(ticker, '|', cast(trade_date AS varchar))) AS unique_keys,
       count(DISTINCT ticker) AS tickers,
       min(trade_date) AS first_day,
       max(trade_date) AS last_day
FROM stock_sentiment.daily_price;

-- 2) ข่าวคู่กับราคาปิดของวันซื้อขายเดียวกัน (วันตามเวลานิวยอร์ก)
SELECT n.ticker,
       p.trade_date,
       p.close,
       n.headline,
       n.source,
       n.published_at
FROM stock_sentiment.clean_news n
JOIN stock_sentiment.daily_price p
  ON p.ticker = n.ticker
 AND p.trade_date = CAST(n.published_at AT TIME ZONE 'America/New_York' AS date)
ORDER BY n.published_at DESC
LIMIT 50;

-- 3) จำนวนข่าวต่อหุ้นต่อวัน คู่กับราคาปิด
SELECT p.ticker,
       p.trade_date,
       p.close,
       count(n.news_id) AS news
FROM stock_sentiment.daily_price p
LEFT JOIN stock_sentiment.clean_news n
  ON n.ticker = p.ticker
 AND CAST(n.published_at AT TIME ZONE 'America/New_York' AS date) = p.trade_date
GROUP BY p.ticker, p.trade_date, p.close
ORDER BY p.trade_date DESC, p.ticker;
