-- Raw: ราคาปิดทุกแถวจากไฟล์ของ F1-02 ตามที่รับมา (append อย่างเดียว, F2-04)
CREATE TABLE IF NOT EXISTS ${catalog}.${db}.raw_daily_price (
  ticker      STRING,
  trade_date  DATE      COMMENT 'วันซื้อขายตามเวลานิวยอร์ก',
  close       DOUBLE,
  source      STRING    COMMENT 'yahoo_finance',
  ingested_at TIMESTAMP COMMENT 'เวลาที่ collector ดึงราคา',
  loaded_at   TIMESTAMP COMMENT 'เวลาที่ Spark เขียนลงตาราง'
)
USING iceberg
PARTITIONED BY (years(trade_date))
COMMENT 'Raw daily close rows from ingestion/price, append-only (F2-04)'
TBLPROPERTIES ('format-version' = '2', 'write.parquet.compression-codec' = 'zstd')
