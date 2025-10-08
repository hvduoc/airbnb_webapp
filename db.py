"""
Cấu hình Database cho Airbnb WebApp
Hỗ trợ SQLite (development) và PostgreSQL (production)
Bao gồm connection pooling và cấu hình tối ưu hiệu suất
"""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy.pool import QueuePool
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

# Cấu hình Database từ environment
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"

# Cấu hình Connection Pool cho Production
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 giờ


def create_database_engine():
    """Tạo database engine với cấu hình tối ưu và fallback an toàn"""
    if DATABASE_URL:
        # Production PostgreSQL với connection pooling
        if DATABASE_URL.startswith("postgresql"):
            try:
                print("🗄️ Đang thử kết nối PostgreSQL Production...")
                engine = create_engine(
                    DATABASE_URL,
                    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
                    poolclass=QueuePool,
                    pool_size=POOL_SIZE,
                    max_overflow=MAX_OVERFLOW,
                    pool_timeout=POOL_TIMEOUT,
                    pool_recycle=POOL_RECYCLE,
                    echo=not PRODUCTION,  # Log SQL queries trong development
                    future=True,
                )
                # Test connection immediately
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print(
                    f"✅ PostgreSQL kết nối thành công (Pool: {POOL_SIZE}, Max: {POOL_SIZE + MAX_OVERFLOW})"
                )
                return engine
            except Exception as e:
                print(f"❌ PostgreSQL thất bại: {e}")
                print("🔄 Fallback về SQLite để ứng dụng có thể chạy...")
                # Fallback to SQLite in production if PostgreSQL fails
                engine = create_engine(
                    "sqlite:///app_fallback.db",
                    connect_args={"check_same_thread": False},
                    echo=not PRODUCTION,
                    future=True,
                )
                print("✅ SQLite Fallback Database đã sẵn sàng")
                return engine
        else:
            # Các database khác
            engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
            print(f"✅ Database Engine đã sẵn sàng: {DATABASE_URL.split('://')[0]}")
    else:
        # Development SQLite
        print("🗄️ Sử dụng SQLite cho Development...")
        engine = create_engine(
            "sqlite:///app.db",
            connect_args={"check_same_thread": False},
            echo=not PRODUCTION,
            future=True,
        )
        print("✅ SQLite Development Database đã sẵn sàng")

    return engine


# Tạo engine với cấu hình production
engine = create_database_engine()


def init_db():
    """Khởi tạo database và tạo tất cả tables"""
    try:
        print("🗄️ Đang khởi tạo database schema...")
        SQLModel.metadata.create_all(engine)
        print("✅ Database schema đã được khởi tạo thành công!")

        # Kiểm tra kết nối database
        with Session(engine) as session:
            # Test query để đảm bảo kết nối hoạt động
            result = session.execute(text("SELECT 1")).fetchone()
            if result:
                print("✅ Kết nối database đã được xác nhận")

    except Exception as e:
        print(f"❌ Lỗi khởi tạo database: {e}")
        raise e


def get_session():
    """FastAPI dependency để lấy database session"""
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            print(f"❌ Lỗi database session: {e}")
            raise e
        finally:
            session.close()


@contextmanager
def get_session_context():
    """Context manager để xử lý session thủ công với error handling"""
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            print(f"❌ Lỗi database context: {e}")
            raise e
        finally:
            session.close()


def check_database_health():
    """Kiểm tra sức khỏe database connection"""
    try:
        with Session(engine) as session:
            session.execute(text("SELECT 1")).fetchone()
            return {"status": "healthy", "message": "Database kết nối thành công"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Database lỗi kết nối: {str(e)}"}


def get_database_info():
    """Lấy thông tin database hiện tại"""
    database_type = "SQLite"
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgresql"):
            database_type = "PostgreSQL"
        elif DATABASE_URL.startswith("mysql"):
            database_type = "MySQL"
        elif DATABASE_URL.startswith("sqlite"):
            database_type = "SQLite"

    return {
        "type": database_type,
        "url": DATABASE_URL if DATABASE_URL else "sqlite:///app.db",
        "production": PRODUCTION,
        "pool_size": POOL_SIZE
        if DATABASE_URL and DATABASE_URL.startswith("postgresql")
        else "N/A",
        "health": check_database_health(),
    }
