#!/usr/bin/env python3
"""
Check database schema to debug foreign key issues
"""

import sqlite3


def check_database_schema():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # List all tables
    print("=== ALL TABLES ===")
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    for table in tables:
        print(f"  {table[0]}")

    # Check extracharge table if exists
    print("\n=== EXTRACHARGE SCHEMA ===")
    try:
        schema = cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='extracharge'"
        ).fetchone()
        if schema:
            print(schema[0])
        else:
            print("Table 'extracharge' not found")
    except Exception as e:
        print(f"Error: {e}")

    # Check extra_charges table if exists
    print("\n=== EXTRA_CHARGES SCHEMA ===")
    try:
        schema = cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='extra_charges'"
        ).fetchone()
        if schema:
            print(schema[0])
        else:
            print("Table 'extra_charges' not found")
    except Exception as e:
        print(f"Error: {e}")

    # Check expense_categories table if exists
    print("\n=== EXPENSE_CATEGORIES SCHEMA ===")
    try:
        schema = cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='expense_categories'"
        ).fetchone()
        if schema:
            print(schema[0])
        else:
            print("Table 'expense_categories' not found")
    except Exception as e:
        print(f"Error: {e}")

    conn.close()


if __name__ == "__main__":
    check_database_schema()
