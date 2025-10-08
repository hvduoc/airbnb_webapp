"""
Production configuration for Railway deployment
"""

import os

from sqlmodel import create_engine

from database import create_tables

# Production database URL (PostgreSQL on Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Railway PostgreSQL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # Fallback to SQLite for local development
    engine = create_engine(
        "sqlite:///app.db", connect_args={"check_same_thread": False}
    )


def init_production_db():
    """Initialize database for production"""
    print("🚀 Initializing production database...")
    create_tables()
    print("✅ Database tables created successfully!")


def create_initial_users():
    """Create initial users for production"""
    from sqlalchemy.orm import Session

    from auth_service import create_user

    with Session(engine) as db:
        try:
            # Tạo admin user
            admin_user = create_user(
                db=db,
                username="admin",
                password="AirbnbAdmin2025!",
                full_name="Quản trị viên",
                role="owner",
                email="admin@airbnb.vn",
                phone="0900000000",
            )
            print(f"✅ Created admin user: {admin_user.username}")

            # Tạo manager user
            manager_user = create_user(
                db=db,
                username="manager1",
                password="Manager2025!",
                full_name="Nguyễn Văn Quản Lý",
                role="manager",
                email="manager@airbnb.vn",
                phone="0901234567",
            )
            print(f"✅ Created manager user: {manager_user.username}")

            # Tạo assistant user
            assistant_user = create_user(
                db=db,
                username="assistant1",
                password="Assistant2025!",
                full_name="Trần Thị Trợ Lý",
                role="assistant",
                email="assistant@airbnb.vn",
                phone="0902345678",
            )
            print(f"✅ Created assistant user: {assistant_user.username}")

        except Exception as e:
            print(f"⚠️ User creation error (may already exist): {e}")


if __name__ == "__main__":
    init_production_db()
    create_initial_users()
    print("🎉 Production setup complete!")
