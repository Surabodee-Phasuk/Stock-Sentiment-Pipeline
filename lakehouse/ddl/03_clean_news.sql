-- Cleaned: ข่าวหนึ่งแถวต่อ (news_id, ticker) หลังตัดซ้ำและ validate (MERGE, F2-03)
-- ข่าวชิ้นเดียวที่เกี่ยวกับหลายหุ้นมีหลายแถว ดู ADR-0007
CREATE TABLE IF NOT EXISTS ${catalog}.${db}.clean_news (
  news_id      STRING,
  ticker       STRING,
  headline     STRING,
  summary      STRING,
  source       STRING    COMMENT 'แหล่งแรกที่เจอข่าวนี้',
  url          STRING,
  published_at TIMESTAMP,
  ingested_at  TIMESTAMP COMMENT 'ingested_at ครั้งแรกที่เจอ',
  cleaned_at   TIMESTAMP COMMENT 'เวลาที่ MERGE เข้าตาราง'
)
USING iceberg
PARTITIONED BY (days(published_at))
COMMENT 'Deduplicated news, key (news_id, ticker), MERGE by F2-03 (ADR-0007)'
TBLPROPERTIES ('format-version' = '2', 'write.parquet.compression-codec' = 'zstd')
