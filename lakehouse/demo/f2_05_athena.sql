-- F2-05: time travel ผ่าน Athena (Iceberg) รันใน workgroup `stock-sentiment` ทีละ query

-- 1) ประวัติ snapshot ของ raw_news (ทุกครั้งที่ Spark Streaming เขียน = 1 snapshot)
SELECT snapshot_id, committed_at, operation, summary
FROM stock_sentiment."raw_news$snapshots"
ORDER BY committed_at;

-- 2) จำนวนข่าว ณ snapshot แรก เทียบกับปัจจุบัน
--    แทน <snapshot_id> ด้วยค่าแถวแรกจาก query 1
SELECT count(*) AS rows_then FROM stock_sentiment.raw_news FOR VERSION AS OF <snapshot_id>;
SELECT count(*) AS rows_now FROM stock_sentiment.raw_news;

-- 3) ย้อนดูตามเวลา (เช่น 1 วันก่อน)
SELECT count(*) AS rows_1_day_ago
FROM stock_sentiment.raw_news
FOR TIMESTAMP AS OF (current_timestamp - interval '1' day);

-- 4) ถ้ารันสคริปต์สาธิตด้วย --keep: ดูตารางสาธิตที่เพิ่มคอลัมน์แล้ว
SELECT snapshot_id, committed_at, operation FROM stock_sentiment."zz_f205_demo$snapshots" ORDER BY committed_at;
SELECT ticker, title, sentiment_hint FROM stock_sentiment.zz_f205_demo LIMIT 10;
-- ลบตารางสาธิตเมื่อดูเสร็จ (ใน Athena ใช้ DROP TABLE ไม่ลบไฟล์บน S3
-- ให้รันสคริปต์อีกครั้งโดยไม่ใส่ --keep แทน สคริปต์จะลบทั้งตารางและไฟล์)
