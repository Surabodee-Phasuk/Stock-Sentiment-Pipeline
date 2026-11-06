-- F2-01: เช็กใน Athena ว่าเห็นและอ่านตาราง Iceberg ครบทั้ง 6 ตาราง
-- เปิด Athena Console → workgroup `stock-sentiment` → database `stock_sentiment`
-- แผงด้านซ้ายต้องขึ้น Tables (6)
-- ตารางยังว่าง ต้องได้ 0 ทุกตัวจนกว่า F2-02 / F2-04 จะเขียนข้อมูลลงมา
--
-- ข้อควรรู้: `SHOW CREATE TABLE` ใช้กับตารางเหล่านี้ไม่ได้ (table has unsupported properties)
-- เช็กว่าเป็น Iceberg จาก Glue แทน:
--   aws glue get-tables --database-name stock_sentiment --region ap-southeast-2 \
--     --query 'TableList[].[Name,Parameters.table_type]' --output table

SELECT 'raw_news' AS t, count(*) AS n FROM stock_sentiment.raw_news
UNION ALL SELECT 'raw_daily_price', count(*) FROM stock_sentiment.raw_daily_price
UNION ALL SELECT 'clean_news', count(*) FROM stock_sentiment.clean_news
UNION ALL SELECT 'news_sentiment', count(*) FROM stock_sentiment.news_sentiment
UNION ALL SELECT 'daily_price', count(*) FROM stock_sentiment.daily_price
UNION ALL SELECT 'sentiment_daily', count(*) FROM stock_sentiment.sentiment_daily;
