-- Cleaned: sentiment ต่อข่าวต่อหุ้นต่อเวอร์ชันโมเดล (F3-01, reprocess F3-04)
-- มี published_at ไว้ partition และ join กับ clean_news ได้โดยไม่ต้องสแกนทั้งตาราง
CREATE TABLE IF NOT EXISTS ${catalog}.${db}.news_sentiment (
  news_id         STRING,
  ticker          STRING,
  published_at    TIMESTAMP,
  sentiment       STRING    COMMENT 'positive | neutral | negative',
  sentiment_score DOUBLE,
  model_name      STRING,
  model_version   STRING,
  processed_at    TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(published_at))
COMMENT 'FinBERT sentiment per news, key (news_id, ticker, model_version) (F3-01, F3-04)'
TBLPROPERTIES ('format-version' = '2', 'write.parquet.compression-codec' = 'zstd')
