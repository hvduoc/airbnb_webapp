"""
Go-Live Import Pipeline Migration
Adds fields to support robust data import and validation
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """
    Add Go-Live import pipeline fields to Booking and ImportLog tables
    """
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🚀 Starting Go-Live Import Pipeline Migration...")
        
        # ===== ADD FIELDS TO BOOKING TABLE =====
        print("📝 Adding new fields to booking table...")
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(booking)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        new_fields = [
            ("source", "VARCHAR(50) DEFAULT 'airbnb'"),
            ("channel", "VARCHAR(100) DEFAULT 'official_csv'"),
            ("external_ref", "VARCHAR(255)"),
            ("imported_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("ingestion_id", "VARCHAR(36)"),
            ("row_hash", "VARCHAR(64)")  # Remove UNIQUE constraint for SQLite compatibility
        ]
        
        for field_name, field_def in new_fields:
            if field_name not in existing_columns:
                alter_sql = f"ALTER TABLE booking ADD COLUMN {field_name} {field_def}"
                cursor.execute(alter_sql)
                print(f"   ✅ Added field: {field_name}")
            else:
                print(f"   ⚠️ Field already exists: {field_name}")
        
        # ===== CREATE INDEXES FOR NEW FIELDS =====
        print("📊 Creating indexes for new fields...")
        
        indexes = [
            ("idx_booking_source", "CREATE INDEX IF NOT EXISTS idx_booking_source ON booking(source)"),
            ("idx_booking_channel", "CREATE INDEX IF NOT EXISTS idx_booking_channel ON booking(channel)"),
            ("idx_booking_imported_at", "CREATE INDEX IF NOT EXISTS idx_booking_imported_at ON booking(imported_at)"),
            ("idx_booking_ingestion_id", "CREATE INDEX IF NOT EXISTS idx_booking_ingestion_id ON booking(ingestion_id)"),
            ("idx_booking_row_hash", "CREATE INDEX IF NOT EXISTS idx_booking_row_hash ON booking(row_hash)"),
            ("idx_booking_source_channel", "CREATE INDEX IF NOT EXISTS idx_booking_source_channel ON booking(source, channel)")
        ]
        
        for idx_name, idx_sql in indexes:
            cursor.execute(idx_sql)
            print(f"   ✅ Created index: {idx_name}")
        
        # ===== RECREATE IMPORTLOG TABLE =====
        print("🗄️ Recreating importlog table with enhanced schema...")
        
        # Drop old table if exists
        cursor.execute("DROP TABLE IF EXISTS importlog")
        
        # Create new table
        create_importlog_sql = """
        CREATE TABLE importlog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(255) NOT NULL,
            source VARCHAR(50) NOT NULL DEFAULT 'airbnb',
            channel VARCHAR(100) NOT NULL DEFAULT 'official_csv',
            ingestion_id VARCHAR(36) NOT NULL UNIQUE,
            
            -- Import statistics
            rows_total INTEGER DEFAULT 0,
            rows_inserted INTEGER DEFAULT 0,
            rows_updated INTEGER DEFAULT 0,
            rows_skipped INTEGER DEFAULT 0,
            rows_errors INTEGER DEFAULT 0,
            
            -- Metadata
            file_size_bytes INTEGER,
            processing_time_seconds REAL,
            error_log_file VARCHAR(255),
            
            -- Audit trail
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
        """
        
        cursor.execute(create_importlog_sql)
        print("   ✅ Created new importlog table")
        
        # Create indexes for importlog
        importlog_indexes = [
            "CREATE INDEX idx_importlog_source_channel ON importlog(source, channel)",
            "CREATE INDEX idx_importlog_created ON importlog(created_at)",
            "CREATE INDEX idx_importlog_ingestion ON importlog(ingestion_id)"
        ]
        
        for idx_sql in importlog_indexes:
            cursor.execute(idx_sql)
        
        print("   ✅ Created importlog indexes")
        
        # ===== COMMIT CHANGES =====
        conn.commit()
        print("✅ Go-Live Import Pipeline Migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()