import os
import re
import sqlite3

# Đường dẫn gốc của project (nơi có main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(BASE_DIR) == "migrations":
    BASE_DIR = os.path.dirname(BASE_DIR)

DB_FILE = os.path.join(BASE_DIR, "app.db")
SQL_FILE = os.path.join(BASE_DIR, "migrations", "expenses_v1.sql")

print("Using DB:", DB_FILE)
print("Using SQL:", SQL_FILE)

with open(SQL_FILE, "r", encoding="utf-8") as f:
    sql_script = f.read()

# Loại bỏ comment kiểu HTML (<!-- ... -->) nếu có
sql_script = re.sub(r"<!--.*?-->", "", sql_script, flags=re.S)

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.executescript(sql_script)
conn.commit()
conn.close()

print("Migration completed successfully.")
