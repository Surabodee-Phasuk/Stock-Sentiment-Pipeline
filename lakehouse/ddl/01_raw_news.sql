-- Raw: ข่าวทุก event จาก Kafka `stock-news` ตามที่รับมา (append อย่างเดียว, F2-02)
-- เก็บ JSON ต้นฉบับไว้ใน raw_value เพื่อ reprocess ได้แม้ schema ของ event เปลี่ยน
CREATE TABLE IF NOT EXISTS ${catalog}.${db}.raw_news (
  news_id         STRING    COMMENT 'sha256 ของ URL ที่ normalize แล้ว',
  ticker          STRING,
  headline        STRING,
  summary         STRING,
  source          STRING    COMMENT 'เช่น rss:yahoo, rss:nasdaq',
  url             STRING,
  published_at    TIMESTAMP,
  ingested_at     TIMESTAMP COMMENT 'เวลาที่ collector ดึงข่าว',
  kafka_partition INT,
  kafka_offset    BIGINT,
  kafka_timestamp TIMESTAMP,
  raw_value       STRING    COMMENT 'JSON ต้นฉบับจาก Kafka',
  loaded_at       TIMESTAMP COMMENT 'เวลาที่ Spark เขียนลงตาราง (วัด latency)'
)
USING iceberg
PARTITIONED BY (days(published_at))
COMMENT 'Raw news events from Kafka stock-news, append-only (F2-02)'
TBLPROPERTIES ('format-version' = '2', 'write.parquet.compression-codec' = 'zstd')
