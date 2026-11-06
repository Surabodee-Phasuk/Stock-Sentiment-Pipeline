-- F2-01: เช็กใน Athena ว่าเห็นตาราง Iceberg ครบทั้ง 6 ตาราง
-- เปิด Athena Console → workgroup `stock-sentiment` → database `stock_sentiment` แล้วรันทีละ query

-- 1) ต้องได้ 6 ตาราง: clean_news, daily_price, news_sentiment, raw_daily_price, raw_news, sentiment_daily
SHOW TABLES IN stock_sentiment;

-- 2) ทุกตารางต้องมี table_type = ICEBERG
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'stock_sentiment'
ORDER BY table_name;

-- 3) query ได้จริง (ตารางยังว่าง ต้องได้ 0 ทุกตัว)
SELECT 'raw_news' AS t, count(*) AS n FROM stock_sentiment.raw_news
UNION ALL SELECT 'raw_daily_price', count(*) FROM stock_sentiment.raw_daily_price
UNION ALL SELECT 'clean_news', count(*) FROM stock_sentiment.clean_news
UNION ALL SELECT 'news_sentiment', count(*) FROM stock_sentiment.news_sentiment
UNION ALL SELECT 'daily_price', count(*) FROM stock_sentiment.daily_price
UNION ALL SELECT 'sentiment_daily', count(*) FROM stock_sentiment.sentiment_daily;

-- 4) ดู schema และ partition ของตารางหลัก
DESCRIBE stock_sentiment.clean_news;
