-- F2-03: duplicate rate ในชั้น Cleaned ต้องเป็น 0% (FR-2.3, NFR-4)
-- คีย์ของ clean_news คือ (news_id, ticker) ตาม ADR-0007
-- รันใน Athena workgroup `stock-sentiment` ทีละ query

-- 1) duplicate rate: ต้องได้ duplicates = 0
SELECT count(*) AS rows,
       count(DISTINCT concat(news_id, '|', ticker)) AS unique_keys,
       count(*) - count(DISTINCT concat(news_id, '|', ticker)) AS duplicates
FROM stock_sentiment.clean_news;

-- 2) เทียบกับ raw: raw มีซ้ำ แต่ clean ต้องไม่มี
SELECT 'raw_news' AS layer, count(*) AS rows,
       count(DISTINCT concat(news_id, '|', ticker)) AS unique_keys
FROM stock_sentiment.raw_news
UNION ALL
SELECT 'clean_news', count(*), count(DISTINCT concat(news_id, '|', ticker))
FROM stock_sentiment.clean_news;

-- 3) ข่าวต่อหุ้นในชั้น Cleaned
SELECT ticker, count(*) AS news
FROM stock_sentiment.clean_news
GROUP BY ticker
ORDER BY ticker;
