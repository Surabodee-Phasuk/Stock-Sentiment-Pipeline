-- Cleaned: ราคาปิดหนึ่งแถวต่อ (ticker, trade_date) (MERGE, F2-04)
CREATE TABLE IF NOT EXISTS ${catalog}.${db}.daily_price (
  ticker      STRING,
  trade_date  DATE,
  close       DOUBLE,
  source      STRING,
  ingested_at TIMESTAMP COMMENT 'ingested_at ของแถวล่าสุดที่ MERGE เข้ามา',
  updated_at  TIMESTAMP COMMENT 'เวลาที่ MERGE ล่าสุด'
)
USING iceberg
PARTITIONED BY (years(trade_date))
COMMENT 'Daily close, key (ticker, trade_date), MERGE by F2-04'
TBLPROPERTIES ('format-version' = '2', 'write.parquet.compression-codec' = 'zstd')
