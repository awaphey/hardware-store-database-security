from pathlib import Path

import pyodbc


ROOT = Path(__file__).resolve().parents[1]
SERVER_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    "DATABASE=master;"
    "Trusted_Connection=yes;"
    "Encrypt=no"
)


def split_sql_batches(sql_text):
    batch = []
    for line in sql_text.splitlines():
        if line.strip().upper() == "GO":
            if batch:
                yield "\n".join(batch).strip()
                batch = []
        else:
            batch.append(line)

    if batch:
        yield "\n".join(batch).strip()


def execute_sql_file(cursor, path):
    sql_text = path.read_text(encoding="utf-8")
    for batch in split_sql_batches(sql_text):
        if batch:
            cursor.execute(batch)


with pyodbc.connect(SERVER_CONNECTION_STRING, autocommit=True) as conn:
    cursor = conn.cursor()
    execute_sql_file(cursor, ROOT / "database" / "schema.sql")
    execute_sql_file(cursor, ROOT / "database" / "seed.sql")

print("HardwareStoreDB schema and seed data were created successfully.")
