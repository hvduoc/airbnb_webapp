import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "app.db")

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

print("== Tables ==")
for (name,) in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print("-", name)

print("\n== Categories sample ==")
cur.execute("SELECT COUNT(*) FROM expense_categories")
print("expense_categories rows:", cur.fetchone()[0])

print("\n== Expenses schema ==")
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='expenses'")
row = cur.fetchone()
print(row[0] if row else "No table 'expenses' found.")

conn.close()
