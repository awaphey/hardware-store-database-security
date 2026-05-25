import os

import pyodbc


DEFAULT_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    "DATABASE=HardwareStoreDB;"
    "Trusted_Connection=yes;"
    "Encrypt=no"
)


connection_string = os.environ.get(
    "HARDWARE_STORE_CONNECTION_STRING",
    DEFAULT_CONNECTION_STRING,
)

with pyodbc.connect(connection_string) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT DB_NAME() AS DatabaseName, @@VERSION AS VersionInfo")
    row = cursor.fetchone()

print(f"Connected database: {row.DatabaseName}")
print(row.VersionInfo)
