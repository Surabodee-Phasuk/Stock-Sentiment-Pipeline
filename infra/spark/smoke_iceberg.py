"""INFRA-03 smoke test: Spark ในเครื่องเขียน/อ่านตาราง Iceberg บน S3 ผ่าน Glue catalog ได้.

รันใน container:
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit infra/spark/smoke_iceberg.py [--keep]

สร้างตารางชั่วคราว `stock_sentiment.zz_infra03_smoke` เขียน 1 แถว อ่านกลับ แล้วลบทิ้ง (PURGE)
ใส่ `--keep` เพื่อเก็บตารางไว้ลอง query ผ่าน Athena แล้วค่อยรันซ้ำโดยไม่มี `--keep` เพื่อลบ
"""

from __future__ import annotations

import argparse

from pyspark.sql import SparkSession

TABLE = "glue.stock_sentiment.zz_infra03_smoke"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep", action="store_true", help="ไม่ลบตารางหลังทดสอบ")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("infra03-smoke-iceberg").getOrCreate()

    spark.sql(f"DROP TABLE IF EXISTS {TABLE} PURGE")
    spark.sql(f"CREATE TABLE {TABLE} (id INT, note STRING) USING iceberg")
    spark.sql(f"INSERT INTO {TABLE} VALUES (1, 'hello from local spark')")

    rows = [tuple(r) for r in spark.sql(f"SELECT id, note FROM {TABLE}").collect()]
    location = spark.sql(f"DESCRIBE TABLE EXTENDED {TABLE}").where(
        "col_name = 'Location'"
    )
    snapshots = spark.sql(f"SELECT count(*) FROM {TABLE}.snapshots").first()[0]

    print(f"rows={rows}")
    print(f"location={location.first()['data_type']}")
    print(f"snapshots={snapshots}")
    if rows != [(1, "hello from local spark")]:
        raise SystemExit("unexpected rows")

    if args.keep:
        print(
            f"kept {TABLE} — try in Athena: SELECT * FROM stock_sentiment.zz_infra03_smoke"
        )
    else:
        spark.sql(f"DROP TABLE {TABLE} PURGE")
        print(f"dropped {TABLE}")

    print("iceberg smoke test passed")
    spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
