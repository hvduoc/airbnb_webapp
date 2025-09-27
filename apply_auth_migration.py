"""
Apply authentication migration using Python
"""
import sqlite3
from pathlib import Path

def apply_auth_migration():
    """Apply authentication tables migration"""
    
    # Read migration SQL
    migration_path = Path("migrations/auth_tables.sql")
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Connect to database
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        # Execute migration
        cursor.executescript(sql_content)
        print("✅ Authentication migration applied successfully!")
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('user', 'usersession')")
        tables = cursor.fetchall()
        print(f"📊 Created tables: {[table[0] for table in tables]}")
        
        # Check admin user created
        cursor.execute("SELECT username, role FROM user WHERE role='admin'")
        admin_users = cursor.fetchall()
        print(f"👤 Admin users: {admin_users}")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    apply_auth_migration()