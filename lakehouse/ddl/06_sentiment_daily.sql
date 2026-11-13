-- Aggregated: sentiment รายวันต่อหุ้นคู่กับราคาปิด (Spark batch, F4-01)
CREATE TABLE IF NOT EXISTS ${catalog}.${db}.sentiment_daily (
  ticker              STRING,
  trade_date          DATE,
  total_news          INT,
  positive_count      INT,
  neutral_count       INT,
  negative_count      INT,
  positive_pct        DOUBLE,
  neutral_pct         DOUBLE,
  negative_pct        DOUBLE,
  avg_sentiment_score DOUBLE,
  close               DOUBLE,
  close_change_pct    DOUBLE,
  model_version       STRING,
  computed_at         TIMESTAMP
)
USING iceberg
PARTITIONED BY (years(trade_date))
COMMENT 'Daily sentiment per ticker joined with close, key (ticker, trade_date, model_version) (F4-01)'
TBLPROPERTIES ('format-version' = '2', 'write.parquet.compression-codec' = 'zstd')
