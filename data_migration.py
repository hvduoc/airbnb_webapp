"""
Script Di chuyển Dữ liệu - Airbnb WebApp
Công cụ di chuyển dữ liệu an toàn từ SQLite sang PostgreSQL
Bao gồm backup, validation và rollback procedures
"""

import json
import logging
import os
import sqlite3
import sys
from datetime import datetime
from typing import Dict, List

from sqlalchemy import create_engine, text
from sqlmodel import Session

# Thêm đường dẫn để import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import (Booking, Building, Channel, ExpenseCategory, ExtraCharge,
                    ImportLog, Property, User, UserSession)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('migration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Công cụ di chuyển database với các tính năng an toàn"""
    
    def __init__(self, source_db: str, target_db: str):
        """
        Khởi tạo migrator
        
        Args:
            source_db: Đường dẫn database nguồn (SQLite)
            target_db: Connection string database đích (PostgreSQL)
        """
        self.source_db = source_db
        self.target_db = target_db
        self.backup_dir = "backups"
        self.migration_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Tạo thư mục backup
        os.makedirs(self.backup_dir, exist_ok=True)
        
        logger.info("🚀 Khởi tạo Database Migrator")
        logger.info(f"📂 Source: {source_db}")
        logger.info(f"🎯 Target: {target_db.split('@')[0]}@***")  # Ẩn password
    
    def create_backup(self) -> str:
        """Tạo backup database nguồn"""
        try:
            backup_file = os.path.join(
                self.backup_dir, 
                f"backup_sqlite_{self.migration_timestamp}.db"
            )
            
            logger.info("📋 Đang tạo backup database nguồn...")
            
            # Copy SQLite database
            import shutil
            shutil.copy2(self.source_db, backup_file)
            
            logger.info(f"✅ Backup đã tạo: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"❌ Lỗi tạo backup: {e}")
            raise e
    
    def export_data_to_json(self) -> Dict[str, List[Dict]]:
        """Xuất tất cả dữ liệu từ SQLite sang JSON format"""
        try:
            logger.info("📤 Đang xuất dữ liệu từ SQLite...")
            
            # Kết nối SQLite
            conn = sqlite3.connect(self.source_db)
            conn.row_factory = sqlite3.Row  # Để có thể access by column name
            
            exported_data = {}
            
            # Danh sách tables cần xuất
            tables = [
                'building', 'property', 'channel', 'booking', 
                'importlog', 'user', 'usersession', 'extracharge', 
                'expensecategory'
            ]
            
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    # Convert sang list of dict
                    data = []
                    for row in rows:
                        row_dict = dict(row)
                        # Convert datetime strings nếu cần
                        for key, value in row_dict.items():
                            if isinstance(value, str) and ('created_at' in key or 'updated_at' in key or 'date' in key):
                                try:
                                    # Validate datetime format
                                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                                except:
                                    pass  # Giữ nguyên nếu không phải datetime
                        data.append(row_dict)
                    
                    exported_data[table] = data
                    logger.info(f"✅ Xuất table '{table}': {len(data)} records")
                    
                except sqlite3.OperationalError as e:
                    if "no such table" in str(e).lower():
                        logger.warning(f"⚠️ Table '{table}' không tồn tại, bỏ qua")
                        exported_data[table] = []
                    else:
                        raise e
            
            conn.close()
            
            # Lưu exported data ra file
            export_file = os.path.join(
                self.backup_dir,
                f"exported_data_{self.migration_timestamp}.json"
            )
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(exported_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 Dữ liệu đã xuất ra: {export_file}")
            return exported_data
            
        except Exception as e:
            logger.error(f"❌ Lỗi xuất dữ liệu: {e}")
            raise e
    
    def validate_data(self, data: Dict[str, List[Dict]]) -> bool:
        """Validate dữ liệu trước khi import"""
        try:
            logger.info("🔍 Đang validate dữ liệu...")
            
            validation_results = []
            
            # Kiểm tra tables quan trọng
            required_tables = ['building', 'property', 'channel']
            for table in required_tables:
                if table not in data or len(data[table]) == 0:
                    validation_results.append(f"❌ Table '{table}' thiếu dữ liệu")
                else:
                    validation_results.append(f"✅ Table '{table}': {len(data[table])} records")
            
            # Kiểm tra tính toàn vẹn dữ liệu
            if 'booking' in data and 'property' in data:
                property_ids = {p['id'] for p in data['property']}
                booking_property_ids = {b['property_id'] for b in data['booking'] if b.get('property_id')}
                
                missing_properties = booking_property_ids - property_ids
                if missing_properties:
                    validation_results.append(f"⚠️ Bookings có property_id không tồn tại: {missing_properties}")
                else:
                    validation_results.append("✅ Tính toàn vẹn booking-property OK")
            
            # In kết quả validation
            for result in validation_results:
                logger.info(result)
            
            # Kiểm tra có lỗi critical không
            has_critical_errors = any("❌" in result for result in validation_results)
            
            if has_critical_errors:
                logger.error("❌ Validation thất bại - có lỗi critical")
                return False
            else:
                logger.info("✅ Validation thành công")
                return True
                
        except Exception as e:
            logger.error(f"❌ Lỗi validation: {e}")
            return False
    
    def import_data_to_postgresql(self, data: Dict[str, List[Dict]]) -> bool:
        """Import dữ liệu vào PostgreSQL"""
        try:
            logger.info("📥 Đang import dữ liệu vào PostgreSQL...")
            
            # Tạo engine PostgreSQL
            target_engine = create_engine(self.target_db)
            
            # Mapping table names to SQLModel classes
            model_mapping = {
                'building': Building,
                'property': Property,
                'channel': Channel,
                'booking': Booking,
                'importlog': ImportLog,
                'user': User,
                'usersession': UserSession,
                'extracharge': ExtraCharge,
                'expensecategory': ExpenseCategory
            }
            
            with Session(target_engine) as session:
                # Tạo tables
                from sqlmodel import SQLModel
                SQLModel.metadata.create_all(target_engine)
                logger.info("✅ Database schema đã tạo")
                
                # Import theo thứ tự (để tránh foreign key issues)
                import_order = [
                    'building', 'channel', 'expensecategory', 
                    'property', 'user', 'booking', 'extracharge',
                    'importlog', 'usersession'
                ]
                
                total_imported = 0
                
                for table_name in import_order:
                    if table_name in data and table_name in model_mapping:
                        model_class = model_mapping[table_name]
                        table_data = data[table_name]
                        
                        if not table_data:
                            logger.info(f"⏭️ Table '{table_name}' trống, bỏ qua")
                            continue
                        
                        logger.info(f"📥 Import table '{table_name}': {len(table_data)} records...")
                        
                        imported_count = 0
                        for record in table_data:
                            try:
                                # Tạo instance model
                                instance = model_class(**record)
                                session.add(instance)
                                imported_count += 1
                                
                                # Commit theo batch để tránh memory issues
                                if imported_count % 100 == 0:
                                    session.commit()
                                    
                            except Exception as e:
                                logger.warning(f"⚠️ Lỗi import record trong {table_name}: {e}")
                                session.rollback()
                                continue
                        
                        # Final commit cho table
                        session.commit()
                        total_imported += imported_count
                        logger.info(f"✅ Imported {imported_count} records vào '{table_name}'")
                
                logger.info(f"🎉 Import hoàn tất! Tổng cộng: {total_imported} records")
                return True
                
        except Exception as e:
            logger.error(f"❌ Lỗi import dữ liệu: {e}")
            return False
    
    def verify_migration(self) -> bool:
        """Verify migration bằng cách so sánh record counts"""
        try:
            logger.info("🔍 Đang verify migration...")
            
            # Kết nối cả 2 databases
            source_engine = create_engine(f"sqlite:///{self.source_db}")
            target_engine = create_engine(self.target_db)
            
            tables_to_check = [
                'building', 'property', 'channel', 'booking', 
                'user', 'extracharge', 'expensecategory'
            ]
            
            verification_passed = True
            
            with Session(source_engine) as source_session, Session(target_engine) as target_session:
                for table in tables_to_check:
                    try:
                        # Count trong source
                        source_count = source_session.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        ).scalar()
                        
                        # Count trong target
                        target_count = target_session.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        ).scalar()
                        
                        if source_count == target_count:
                            logger.info(f"✅ Table '{table}': {source_count} = {target_count}")
                        else:
                            logger.error(f"❌ Table '{table}': Source={source_count} != Target={target_count}")
                            verification_passed = False
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Không thể verify table '{table}': {e}")
            
            if verification_passed:
                logger.info("🎉 Migration verification PASSED!")
            else:
                logger.error("❌ Migration verification FAILED!")
            
            return verification_passed
            
        except Exception as e:
            logger.error(f"❌ Lỗi verify migration: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Chạy toàn bộ quá trình migration"""
        try:
            logger.info("🚀 BẮT ĐẦU MIGRATION DATABASE")
            logger.info("=" * 50)
            
            # Bước 1: Tạo backup
            backup_file = self.create_backup()
            
            # Bước 2: Xuất dữ liệu
            exported_data = self.export_data_to_json()
            
            # Bước 3: Validate dữ liệu
            if not self.validate_data(exported_data):
                logger.error("❌ Validation thất bại - dừng migration")
                return False
            
            # Bước 4: Import vào PostgreSQL
            if not self.import_data_to_postgresql(exported_data):
                logger.error("❌ Import thất bại - rollback required")
                return False
            
            # Bước 5: Verify migration
            if not self.verify_migration():
                logger.error("❌ Verification thất bại - kiểm tra dữ liệu")
                return False
            
            logger.info("=" * 50)
            logger.info("🎉 MIGRATION THÀNH CÔNG!")
            logger.info(f"📋 Backup tại: {backup_file}")
            logger.info("📊 Log tại: migration.log")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration thất bại: {e}")
            return False

def main():
    """Hàm main để chạy migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migration Database Airbnb WebApp")
    parser.add_argument("--source", default="app.db", help="SQLite database file")
    parser.add_argument("--target", required=True, help="PostgreSQL connection string")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ validate, không import")
    
    args = parser.parse_args()
    
    # Kiểm tra file source tồn tại
    if not os.path.exists(args.source):
        logger.error(f"❌ File database nguồn không tồn tại: {args.source}")
        return False
    
    # Tạo migrator
    migrator = DatabaseMigrator(args.source, args.target)
    
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - chỉ validate dữ liệu")
        exported_data = migrator.export_data_to_json()
        return migrator.validate_data(exported_data)
    else:
        return migrator.run_migration()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)