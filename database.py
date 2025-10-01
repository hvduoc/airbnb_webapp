"""
Database Models cho hệ thống Payment Ledger
Sử dụng SQLite để lưu trữ dữ liệu bền vững
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Tạo database file
DATABASE_URL = "sqlite:///./payment_ledger.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """Bảng người dùng"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # assistant, manager, owner
    phone = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(Base):
    """Bảng ghi nhận thu"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String(50), nullable=False)
    guest_name = Column(String(100), nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_collected = Column(Float, nullable=False)
    payment_method = Column(String(30), nullable=False)
    collected_by = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    receipt_image = Column(String(255), nullable=True)
    status = Column(String(20), default="completed")
    added_by_user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Handover(Base):
    """Bảng bàn giao tiền mặt"""
    __tablename__ = "handovers"
    
    id = Column(Integer, primary_key=True, index=True)
    handover_by_user_id = Column(Integer, nullable=False)
    recipient_user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    handover_image = Column(String(255), nullable=True)
    status = Column(String(20), default="completed")
    signature_status = Column(String(20), default="pending")  # pending, signed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Tạo tất cả các bảng
def create_tables():
    """Tạo tất cả các bảng trong database"""
    Base.metadata.create_all(bind=engine)

# Dependency để lấy database session
def get_db():
    """Lấy database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    print("✅ Đã tạo database và các bảng thành công!")