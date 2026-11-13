"""F2-01: สร้างตาราง Iceberg ทั้งสามชั้นใน Glue จากไฟล์ `lakehouse/ddl/*.sql` (รันซ้ำได้).

รันใน container `spark` (ต้องตั้งค่า AWS แล้ว):
    docker compose -f infra/docker-compose.yml exec spark \
        /opt/spark/bin/spark-submit lakehouse/ddl/create_tables.py

ดู SQL ที่จะรันโดยไม่ต่อ AWS (ไม่ต้องมี Spark):
    python -m lakehouse.ddl.create_tables --dry-run

ทุกไฟล์ใช้ `CREATE TABLE IF NOT EXISTS` รันซ้ำจึงไม่ลบหรือแก้ตารางที่มีอยู่
ถ้าจะเปลี่ยน schema ของตารางที่มีข้อมูลแล้ว ให้ใช้ ALTER TABLE (schema evolution, F2-05) ไม่ใช่แก้ไฟล์นี้แล้วรันใหม่
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

DDL_DIR = Path(__file__).resolve().parent
DEFAULT_CATALOG = "glue"
DEFAULT_DATABASE = "stock_sentiment"
_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+\S+\.\S+\.(\w+)", re.IGNORECASE
)


@dataclass(frozen=True)
class Statement:
    file: str
    table: str
    sql: str


def load_statements(
    catalog: str = DEFAULT_CATALOG,
    database: str = DEFAULT_DATABASE,
    ddl_dir: Path = DDL_DIR,
) -> list[Statement]:
    """อ่านไฟล์ `NN_<table>.sql` ตามลำดับเลข แทน `${catalog}` / `${db}` แล้วตัด comment ออก."""
    statements: list[Statement] = []
    for path in sorted(ddl_dir.glob("[0-9][0-9]_*.sql")):
        text = path.read_text(encoding="utf-8")
        sql = "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("--")
        ).strip()
        sql = sql.replace("${catalog}", catalog).replace("${db}", database)
        match = _TABLE_RE.search(sql)
        if not match:
            raise ValueError(f"{path.name}: expected CREATE TABLE IF NOT EXISTS")
        statements.append(Statement(file=path.name, table=match.group(1), sql=sql))
    if not statements:
        raise ValueError(f"no DDL files in {ddl_dir}")
    return statements


def apply(statements: Sequence[Statement], catalog: str, database: str) -> int:
    # import ตอนใช้ เพื่อให้ --dry-run และ unit test ไม่ต้องมี pyspark
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("f2-01-create-tables").getOrCreate()
    try:
        before = {
            row.tableName
            for row in spark.sql(f"SHOW TABLES IN {catalog}.{database}").collect()
        }
        for stmt in statements:
            spark.sql(stmt.sql)
            state = "exists " if stmt.table in before else "created"
            print(f"{state} {catalog}.{database}.{stmt.table}  ({stmt.file})")

        after = {
            row.tableName
            for row in spark.sql(f"SHOW TABLES IN {catalog}.{database}").collect()
        }
        missing = [s.table for s in statements if s.table not in after]
        if missing:
            print(f"missing after apply: {missing}", file=sys.stderr)
            return 1

        for stmt in statements:
            table = f"{catalog}.{database}.{stmt.table}"
            columns = []
            for r in spark.sql(f"DESCRIBE TABLE {table}").collect():
                # หลังรายชื่อคอลัมน์จะมีแถวว่างตามด้วยส่วน "# Partitioning"
                if not r.col_name or r.col_name.startswith("#"):
                    break
                columns.append(r.col_name)
            partition = [
                r.data_type
                for r in spark.sql(f"DESCRIBE TABLE EXTENDED {table}").collect()
                if r.col_name.startswith("Part ")
            ]
            print(f"  {stmt.table}: {len(columns)} columns, partition {partition}")
        print(f"all {len(statements)} tables ready in {catalog}.{database}")
        return 0
    finally:
        spark.stop()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create Iceberg tables (F2-01)")
    parser.add_argument("--catalog", default=DEFAULT_CATALOG)
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument(
        "--dry-run", action="store_true", help="print SQL only, no Spark/AWS"
    )
    args = parser.parse_args(argv)

    statements = load_statements(args.catalog, args.database)
    if args.dry_run:
        for stmt in statements:
            print(f"-- {stmt.file}\n{stmt.sql};\n")
        return 0
    return apply(statements, args.catalog, args.database)


if __name__ == "__main__":
    raise SystemExit(main())
