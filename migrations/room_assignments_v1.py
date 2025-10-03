"""
Database migration for Room Assignment tracking
Date: 2025-09-25
Purpose: Add room_assignments table to track booking room vs actual room cases
"""

import os
import sqlite3


def run_migration():
    """
    Create room_assignments table
    """
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create room_assignments table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS room_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            booked_room TEXT,
            actual_room TEXT,
            revenue_attribution TEXT DEFAULT 'actual_room',
            change_reason TEXT,
            changed_date DATE,
            changed_by TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (booking_id) REFERENCES booking(id) ON DELETE CASCADE
        );
        """
        
        cursor.execute(create_table_sql)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_room_assignments_booking_id ON room_assignments(booking_id);",
            "CREATE INDEX IF NOT EXISTS idx_room_assignments_booked_room ON room_assignments(booked_room);", 
            "CREATE INDEX IF NOT EXISTS idx_room_assignments_actual_room ON room_assignments(actual_room);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        print("✅ Room assignments table created successfully")
        print("✅ Indexes created successfully")
        
        # Verify table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='room_assignments';")
        if cursor.fetchone():
            print("✅ Table verification passed")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(room_assignments);")
            columns = cursor.fetchall()
            print("\n📋 Table structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            return True
        else:
            print("❌ Table verification failed")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting room assignments migration...")
    success = run_migration()
    
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        exit(1)