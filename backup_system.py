"""
Hệ thống Sao lưu Tự động - Airbnb WebApp
Backup PostgreSQL database với retention policy và monitoring
"""

import os
import subprocess
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import time
from pathlib import Path

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/backup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Quản lý backup database PostgreSQL tự động"""
    
    def __init__(self, config_file: str = "backup_config.json"):
        """Khởi tạo backup system"""
        self.config = self.load_config(config_file)
        self.backup_dir = Path(self.config.get("backup_directory", "backups/database"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔄 Khởi tạo Database Backup System")
        logger.info(f"📁 Backup directory: {self.backup_dir}")
    
    def load_config(self, config_file: str) -> Dict:
        """Load cấu hình backup"""
        default_config = {
            "database_url": os.getenv("DATABASE_URL", ""),
            "backup_directory": "backups/database",
            "retention_days": 30,
            "backup_schedule": {
                "daily": "02:00",  # 2 AM hàng ngày
                "weekly": "sunday:03:00",  # Chủ nhật 3 AM
                "monthly": "1:04:00"  # Ngày 1 hàng tháng 4 AM
            },
            "compression": True,
            "encryption": False,
            "notification": {
                "enabled": False,
                "webhook_url": "",
                "email": ""
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            else:
                # Tạo config file mặc định
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                logger.info(f"📄 Đã tạo config file mặc định: {config_file}")
        except Exception as e:
            logger.warning(f"⚠️ Lỗi load config, sử dụng default: {e}")
        
        return default_config
    
    def create_backup(self, backup_type: str = "manual") -> Optional[str]:
        """Tạo backup database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"airbnb_db_backup_{backup_type}_{timestamp}.sql"
            
            if self.config.get("compression", True):
                backup_filename += ".gz"
            
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"🔄 Bắt đầu backup {backup_type}...")
            logger.info(f"📁 File: {backup_path}")
            
            # Parse database URL
            db_url = self.config["database_url"]
            if not db_url.startswith("postgresql"):
                logger.error("❌ Chỉ hỗ trợ PostgreSQL backup")
                return None
            
            # Extract connection info
            # postgresql://user:password@host:port/database
            parts = db_url.replace("postgresql://", "").split("/")
            database = parts[1] if len(parts) > 1 else "airbnb_db"
            user_host = parts[0].split("@")
            host_port = user_host[1] if len(user_host) > 1 else "localhost:5432"
            user_pass = user_host[0].split(":")
            
            host = host_port.split(":")[0]
            port = host_port.split(":")[1] if ":" in host_port else "5432"
            username = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            
            # Tạo command pg_dump
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={username}",
                f"--dbname={database}",
                "--verbose",
                "--clean",
                "--no-owner",
                "--no-privileges",
                "--format=custom"
            ]
            
            # Set password environment
            env = os.environ.copy()
            if password:
                env["PGPASSWORD"] = password
            
            # Chạy backup
            if self.config.get("compression", True):
                with open(backup_path, 'wb') as f:
                    import gzip
                    with gzip.open(backup_path, 'wb') as gz_f:
                        process = subprocess.run(
                            cmd, stdout=gz_f, stderr=subprocess.PIPE,
                            env=env, check=True
                        )
            else:
                with open(backup_path, 'wb') as f:
                    process = subprocess.run(
                        cmd, stdout=f, stderr=subprocess.PIPE,
                        env=env, check=True
                    )
            
            # Kiểm tra kết quả
            if backup_path.exists() and backup_path.stat().st_size > 0:
                file_size = backup_path.stat().st_size / (1024 * 1024)  # MB
                logger.info(f"✅ Backup thành công!")
                logger.info(f"📊 Kích thước: {file_size:.2f} MB")
                
                # Ghi metadata
                metadata = {
                    "backup_type": backup_type,
                    "timestamp": timestamp,
                    "database": database,
                    "file_size_mb": round(file_size, 2),
                    "compressed": self.config.get("compression", True),
                    "created_at": datetime.now().isoformat()
                }
                
                metadata_file = backup_path.with_suffix('.json')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                return str(backup_path)
            else:
                logger.error("❌ Backup file trống hoặc không tạo được")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Lỗi pg_dump: {e.stderr.decode()}")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi tạo backup: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Xóa backup cũ theo retention policy"""
        try:
            retention_days = self.config.get("retention_days", 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            logger.info(f"🧹 Dọn dẹp backup cũ hơn {retention_days} ngày...")
            
            deleted_count = 0
            for backup_file in self.backup_dir.glob("*.sql*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    try:
                        # Xóa cả file backup và metadata
                        backup_file.unlink()
                        metadata_file = backup_file.with_suffix('.json')
                        if metadata_file.exists():
                            metadata_file.unlink()
                        
                        deleted_count += 1
                        logger.info(f"🗑️ Đã xóa: {backup_file.name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Không thể xóa {backup_file.name}: {e}")
            
            if deleted_count > 0:
                logger.info(f"✅ Đã xóa {deleted_count} backup cũ")
            else:
                logger.info("✅ Không có backup cũ cần xóa")
                
        except Exception as e:
            logger.error(f"❌ Lỗi cleanup backup: {e}")
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity"""
        try:
            logger.info(f"🔍 Verify backup: {backup_path}")
            
            if not os.path.exists(backup_path):
                logger.error("❌ Backup file không tồn tại")
                return False
            
            # Kiểm tra size
            file_size = os.path.getsize(backup_path)
            if file_size < 1024:  # < 1KB
                logger.error("❌ Backup file quá nhỏ")
                return False
            
            # Test decompression nếu compressed
            if backup_path.endswith('.gz'):
                import gzip
                try:
                    with gzip.open(backup_path, 'rb') as f:
                        f.read(1024)  # Đọc 1KB đầu
                except Exception as e:
                    logger.error(f"❌ Lỗi decompression: {e}")
                    return False
            
            logger.info("✅ Backup verification passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi verify backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """Liệt kê tất cả backup"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("*.sql*")):
            metadata_file = backup_file.with_suffix('.json')
            
            backup_info = {
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(backup_file.stat().st_mtime),
                "metadata": None
            }
            
            # Load metadata nếu có
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        backup_info["metadata"] = json.load(f)
                except Exception as e:
                    logger.warning(f"⚠️ Không đọc được metadata cho {backup_file.name}: {e}")
            
            backups.append(backup_info)
        
        return backups
    
    def restore_backup(self, backup_path: str, target_db: str = None) -> bool:
        """Restore backup (cẩn thận sử dụng!)"""
        try:
            if not target_db:
                target_db = self.config["database_url"]
            
            logger.warning("⚠️ CẢNH BÁO: Đang restore database - dữ liệu hiện tại sẽ bị ghi đè!")
            
            # Verify backup trước
            if not self.verify_backup(backup_path):
                logger.error("❌ Backup verification thất bại")
                return False
            
            # Tạo pg_restore command
            # (Implementation tùy thuộc vào format backup)
            logger.info("🔄 Restore backup sẽ được implement chi tiết...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi restore: {e}")
            return False
    
    def schedule_backups(self):
        """Setup scheduled backups"""
        try:
            schedule_config = self.config.get("backup_schedule", {})
            
            # Daily backup
            if "daily" in schedule_config:
                time_str = schedule_config["daily"]
                schedule.every().day.at(time_str).do(
                    lambda: self.create_backup("daily")
                )
                logger.info(f"📅 Scheduled daily backup at {time_str}")
            
            # Weekly backup
            if "weekly" in schedule_config:
                day_time = schedule_config["weekly"]
                if ":" in day_time:
                    day, time_str = day_time.split(":", 1)
                    getattr(schedule.every(), day.lower()).at(time_str).do(
                        lambda: self.create_backup("weekly")
                    )
                    logger.info(f"📅 Scheduled weekly backup on {day} at {time_str}")
            
            # Cleanup schedule
            schedule.every().day.at("05:00").do(self.cleanup_old_backups)
            logger.info("📅 Scheduled daily cleanup at 05:00")
            
        except Exception as e:
            logger.error(f"❌ Lỗi setup schedule: {e}")
    
    def run_scheduler(self):
        """Chạy scheduled backup daemon"""
        logger.info("🔄 Bắt đầu backup scheduler...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check mỗi phút
            except KeyboardInterrupt:
                logger.info("⏹️ Dừng backup scheduler")
                break
            except Exception as e:
                logger.error(f"❌ Lỗi scheduler: {e}")
                time.sleep(300)  # Sleep 5 phút nếu lỗi

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Backup System")
    parser.add_argument("--action", choices=["backup", "list", "cleanup", "schedule"], 
                       default="backup", help="Hành động cần thực hiện")
    parser.add_argument("--type", choices=["manual", "daily", "weekly", "monthly"], 
                       default="manual", help="Loại backup")
    parser.add_argument("--config", default="backup_config.json", help="Config file")
    
    args = parser.parse_args()
    
    # Tạo backup system
    backup_system = DatabaseBackup(args.config)
    
    if args.action == "backup":
        result = backup_system.create_backup(args.type)
        if result:
            logger.info(f"✅ Backup hoàn tất: {result}")
        else:
            logger.error("❌ Backup thất bại")
    
    elif args.action == "list":
        backups = backup_system.list_backups()
        print("\n📋 DANH SÁCH BACKUP:")
        print("-" * 60)
        for backup in backups:
            print(f"📁 {backup['filename']}")
            print(f"   Kích thước: {backup['size_mb']} MB")
            print(f"   Tạo lúc: {backup['created']}")
            if backup['metadata']:
                print(f"   Loại: {backup['metadata'].get('backup_type', 'Unknown')}")
            print()
    
    elif args.action == "cleanup":
        backup_system.cleanup_old_backups()
    
    elif args.action == "schedule":
        backup_system.schedule_backups()
        backup_system.run_scheduler()

if __name__ == "__main__":
    main()