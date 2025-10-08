"""
Models Database cho Airbnb WebApp - Optimized cho Production
Bao gồm indexing, foreign keys, và performance optimization
Việt hóa hoàn toàn với cấu hình production-ready
"""

import hashlib
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Index, SQLModel

# ============ AUTHENTICATION MODELS - CÓ INDEX TỐI ƯU ============

class User(SQLModel, table=True):
    """Model User với authentication và role-based access - Optimized"""
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    full_name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    
    # Role-based access control - với index
    role: str = Field(default="user", index=True, max_length=50)  # Index cho role queries
    is_active: bool = Field(default=True, index=True)  # Index cho active user queries
    is_verified: bool = Field(default=False)
    
    # Audit trail - với index cho reporting
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None, index=True)  # Index cho login analytics
    
    # Property access control
    accessible_properties: Optional[str] = Field(default="[]")  # JSON string
    
    # Phone và email cho contact
    phone: Optional[str] = Field(default=None, max_length=20)
    
    class Config:
        # Composite indexes cho performance
        indexes = [
            Index("idx_user_active_role", "is_active", "role"),  # Cho role-based queries
            Index("idx_user_login_activity", "last_login", "is_active"),  # Cho analytics
        ]

class UserSession(SQLModel, table=True):
    """Theo dõi user sessions cho bảo mật - Optimized"""
    __tablename__ = "usersession"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    token_jti: str = Field(unique=True, max_length=255)  # JWT ID tracking
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(index=True)  # Index cho cleanup expired sessions
    is_active: bool = Field(default=True, index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 compatible
    user_agent: Optional[str] = Field(default=None, max_length=500)
    
    class Config:
        indexes = [
            Index("idx_session_cleanup", "expires_at", "is_active"),  # Cho cleanup job
            Index("idx_session_user_active", "user_id", "is_active"),  # User sessions
        ]

# ============ BUSINESS MODELS - CÓ INDEX TỐI ƯU ============

class ExtraCharge(SQLModel, table=True):
    """Phụ phí căn hộ - Optimized với indexes"""
    __tablename__ = "extra_charges"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id", index=True)  # Index cho property queries
    charge_name: str = Field(max_length=255)
    charge_amount: int
    charge_month: str = Field(index=True, max_length=7)  # YYYY-MM format, index cho monthly reports
    charge_note: Optional[str] = Field(default=None, max_length=1000)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="expense_categories.id", index=True)
    
    class Config:
        indexes = [
            Index("idx_charge_property_month", "property_id", "charge_month"),  # Reports theo property + tháng
            Index("idx_charge_category_month", "category_id", "charge_month"),  # Reports theo category + tháng
        ]

class Building(SQLModel, table=True):
    """Tòa nhà - Optimized"""
    __tablename__ = "building"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    building_name: str = Field(max_length=255, index=True)  # Index cho search
    building_code: Optional[str] = Field(default=None, max_length=50, unique=True)  # Unique code
    address: Optional[str] = Field(default=None, max_length=500)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Tọa độ cho tòa nhà
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)

class Property(SQLModel, table=True):
    """Căn hộ - Optimized với indexes cho booking performance"""
    __tablename__ = "property"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    building_id: Optional[int] = Field(default=None, foreign_key="building.id", index=True)  # Index cho building queries
    building_name: Optional[str] = Field(default=None, max_length=255)
    room_number: Optional[str] = Field(default=None, max_length=20, index=True)  # Index cho room search
    room_type: Optional[str] = Field(default=None, max_length=50, index=True)  # Index cho type filtering
    area_sqm: Optional[float] = Field(default=None)
    price_per_night: Optional[int] = Field(default=None, index=True)  # Index cho price queries
    max_guests: Optional[int] = Field(default=None)
    
    # Property status
    is_active: bool = Field(default=True, index=True)  # Index cho active properties
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    class Config:
        indexes = [
            Index("idx_property_building_active", "building_id", "is_active"),  # Active properties per building
            Index("idx_property_type_price", "room_type", "price_per_night"),  # Filter by type + price
            Index("idx_property_search", "building_name", "room_number"),  # Property search
        ]
    building_code: Optional[str] = None

    property_name: str
    airbnb_name: Optional[str] = None
    unit_number: Optional[str] = None
    unit_short: Optional[str] = None
    property_short: Optional[str] = None

    address: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    # THÊM MỚI: Tọa độ riêng cho căn hộ nếu cần
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)

class Channel(SQLModel, table=True):
    """Kênh đặt phòng - Optimized"""
    __tablename__ = "channel"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_name: str = Field(max_length=100, unique=True, index=True)  # Index cho channel lookup
    is_active: bool = Field(default=True, index=True)
    commission_rate: Optional[float] = Field(default=None)  # Phần trăm hoa hồng
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Booking(SQLModel, table=True):
    """Booking - Model quan trọng nhất, cần tối ưu cao"""
    __tablename__ = "booking"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    confirmation_code: Optional[str] = Field(default=None, max_length=50, unique=True, index=True)  # Unique + index
    
    # Foreign keys với indexes
    property_id: Optional[int] = Field(default=None, foreign_key="property.id", index=True)
    channel_id: Optional[int] = Field(default=None, foreign_key="channel.id", index=True)
    
    # Ngày tháng - QUAN TRỌNG cho performance
    start_date: Optional[date] = Field(default=None, index=True)  # Index cho date range queries
    end_date: Optional[date] = Field(default=None, index=True)    # Index cho date range queries
    booking_date: Optional[date] = Field(default=None, index=True)  # Index cho booking analytics
    
    # Booking details
    num_nights: Optional[int] = Field(default=None)
    num_adults: Optional[int] = Field(default=None)
    num_children: Optional[int] = Field(default=None)
    num_infants: Optional[int] = Field(default=None)
    
    # Status và financials
    status: Optional[str] = Field(default=None, max_length=50, index=True)  # Index cho status filtering
    total_payout_vnd: Optional[int] = Field(default=None, index=True)  # Index cho revenue queries
    
    # Guest information
    guest_name: Optional[str] = Field(default=None, max_length=255)
    guest_contact: Optional[str] = Field(default=None, max_length=255)
    
    # Audit trail
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Go-Live Import Pipeline Fields - New for data source tracking
    source: Optional[str] = Field(default="airbnb", max_length=50, index=True)  # "airbnb", "offline"
    channel: Optional[str] = Field(default="official_csv", max_length=100, index=True)  # "official_csv", "facebook", "zalo"
    external_ref: Optional[str] = Field(default=None, max_length=255)  # ID cho offline bookings
    imported_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)  # Import timestamp
    ingestion_id: Optional[str] = Field(default=None, max_length=36, index=True)  # UUID cho import batch
    row_hash: Optional[str] = Field(default=None, max_length=64, unique=True, index=True)  # SHA-256 hash cho idempotency
    
    class Config:
        indexes = [
            # Core performance indexes
            Index("idx_booking_dates", "start_date", "end_date"),  # Date range queries
            Index("idx_booking_property_dates", "property_id", "start_date", "end_date"),  # Property availability
            Index("idx_booking_revenue", "property_id", "booking_date", "total_payout_vnd"),  # Revenue reports
            Index("idx_booking_channel_status", "channel_id", "status"),  # Channel performance
            Index("idx_booking_monthly", "property_id", "booking_date"),  # Monthly reports
            # Go-Live Import Pipeline indexes
            Index("idx_booking_source_channel", "source", "channel"),  # Data source tracking
            Index("idx_booking_ingestion", "ingestion_id", "imported_at"),  # Import batch tracking
            Index("idx_booking_hash", "row_hash"),  # Idempotency check
        ]
    
    def generate_row_hash(self) -> str:
        """Generate SHA-256 hash for idempotency check"""
        hash_data = f"{self.guest_name or ''}-{self.start_date or ''}-{self.total_payout_vnd or 0}-{self.property_id or 0}"
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def set_import_metadata(self, source: str, channel: str, ingestion_id: str, external_ref: str = None):
        """Set import metadata fields"""
        self.source = source
        self.channel = channel  
        self.ingestion_id = ingestion_id
        self.external_ref = external_ref
        self.imported_at = datetime.utcnow()
        self.row_hash = self.generate_row_hash()
    listing_raw: Optional[str] = None
    salesperson_id: Optional[int] = Field(default=None, foreign_key="salesperson.id")
    notes: Optional[str] = None    

class ImportLog(SQLModel, table=True):
    """Log import CSV - Enhanced cho Go-Live pipeline"""
    __tablename__ = "importlog"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    source: str = Field(default="upload-form", max_length=50, index=True)  # "airbnb", "offline"
    channel: str = Field(default="official_csv", max_length=100, index=True)  # "official_csv", "facebook", "zalo"
    ingestion_id: str = Field(max_length=36, unique=True, index=True)  # UUID cho import batch
    
    # Import statistics
    rows_total: int = Field(default=0)
    rows_inserted: int = Field(default=0)
    rows_updated: int = Field(default=0)
    rows_skipped: int = Field(default=0)  # Duplicate/invalid rows
    rows_errors: int = Field(default=0)  # Validation errors
    
    # Metadata
    file_size_bytes: Optional[int] = Field(default=None)
    processing_time_seconds: Optional[float] = Field(default=None)
    error_log_file: Optional[str] = Field(default=None, max_length=255)  # Path to error CSV
    
    # Audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: Optional[datetime] = Field(default=None)
    
    class Config:
        indexes = [
            Index("idx_importlog_source_channel", "source", "channel"),
            Index("idx_importlog_created", "created_at"),
            Index("idx_importlog_ingestion", "ingestion_id"),
        ]
    started_at: datetime
    finished_at: datetime
    status: str
    message: Optional[str] = None

class Salesperson(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    commission_rate: float
    is_active: bool = Field(default=True)
    
    # THÊM 2 TRƯỜNG MỚI NÀY
    email: Optional[str] = Field(default=None, unique=True, index=True)
    phone: Optional[str] = Field(default=None)

from datetime import datetime
from typing import Optional

# ==== ENHANCED OPEX MODELS - Optimized for performance ====
from sqlmodel import Column, Field, Index, SQLModel, String


class ExpenseCategory(SQLModel, table=True):
    """Danh mục chi phí - Optimized for frequent lookups"""
    __tablename__ = "expense_categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)  # Index cho category lookups
    parent_id: Optional[int] = Field(default=None, foreign_key="expense_categories.id", index=True)
    is_fixed: int = Field(default=0, index=True)  # Index cho fixed/variable filtering
    
    class Config:
        indexes = [
            Index("idx_expense_cat_hierarchy", "parent_id", "name"),  # Category hierarchy
        ]

class Expense(SQLModel, table=True):
    """Chi phí - Optimized for financial reporting"""
    __tablename__ = "expenses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str = Field(index=True)  # Index cho date queries
    month: str = Field(sa_column=Column(String, index=True))  # Index cho monthly reports
    category_id: int = Field(foreign_key="expense_categories.id", index=True)  # Index cho category queries
    amount: int = Field(index=True)  # Index cho amount-based queries
    vendor: Optional[str] = Field(default=None, max_length=255, index=True)  # Index cho vendor analysis
    note: Optional[str] = Field(default=None, max_length=500)
    building_id: Optional[int] = Field(default=None, index=True)  # Index cho building reports
    property_id: Optional[int] = Field(default=None, index=True)  # Index cho property reports
    allocation_method: str = Field(default="direct", max_length=50, index=True)  # Index cho allocation analysis
    allocation_basis_note: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        indexes = [
            # Core financial reporting indexes
            Index("idx_expense_property_month", "property_id", "month"),  # Property monthly reports
            Index("idx_expense_building_month", "building_id", "month"),  # Building monthly reports
            Index("idx_expense_category_month", "category_id", "month"),  # Category analysis
            Index("idx_expense_vendor_month", "vendor", "month", "amount"),  # Vendor performance
            Index("idx_expense_allocation", "allocation_method", "building_id", "property_id"),  # Allocation queries
        ]

class RecurringExpense(SQLModel, table=True):
    """Chi phí định kỳ - Optimized for automation"""
    __tablename__ = "recurring_expenses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="expense_categories.id", index=True)
    amount: int = Field(index=True)  # Index cho amount queries
    vendor: Optional[str] = Field(default=None, max_length=255, index=True)
    note: Optional[str] = Field(default=None, max_length=500)
    building_id: Optional[int] = Field(default=None, index=True)
    property_id: Optional[int] = Field(default=None, index=True)
    allocation_method: str = Field(default="per_property", max_length=50)
    start_month: str = Field(index=True)  # Index cho scheduling
    end_month: Optional[str] = Field(default=None, index=True)  # Index cho active recurring
    day_of_month: int = Field(default=1, index=True)  # Index cho scheduling
    is_active: int = Field(default=1, index=True)  # Index cho active filtering
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        indexes = [
            Index("idx_recurring_active", "is_active", "start_month", "end_month"),  # Active recurring expenses
            Index("idx_recurring_schedule", "day_of_month", "is_active"),  # Scheduling automation
        ]

class ExpenseAllocation(SQLModel, table=True):
    """Phân bổ chi phí - Optimized for allocation calculations"""
    __tablename__ = "expense_allocations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    expense_id: int = Field(foreign_key="expenses.id", index=True)  # Index cho expense lookups
    property_id: int = Field(index=True)  # Index cho property allocations
    month: str = Field(index=True)  # Index cho monthly reports
    allocated_amount: int = Field(index=True)  # Index cho amount analysis
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        indexes = [
            Index("idx_allocation_expense_property", "expense_id", "property_id"),  # Allocation calculations
            Index("idx_allocation_property_month", "property_id", "month"),  # Property monthly allocations
        ]

# ==== /ENHANCED OPEX MODELS ====

class ImportLog(SQLModel, table=True):
    """Log import CSV - Optimized for analytics"""
    __tablename__ = "import_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255, index=True)  # Index cho file tracking
    imported_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Index cho time-based queries
    rows_processed: int = Field(default=0, index=True)  # Index cho analytics
    rows_successful: int = Field(default=0)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)  # Index cho user tracking
    
    class Config:
        indexes = [
            Index("idx_import_user_date", "user_id", "imported_at"),  # User import history
            Index("idx_import_performance", "imported_at", "rows_processed"),  # Performance tracking
        ]
# ==== /OPEX MODELS ====

# ============ ROOM ASSIGNMENT MODELS ============
class RoomAssignment(SQLModel, table=True):
    """
    Track room assignments for bookings
    Handles cases where booked room != actual room (203 vs 303)
    """
    __tablename__ = "room_assignments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="booking.id", index=True)
    
    # Room information
    booked_room: Optional[str] = Field(default=None)  # Room originally booked (e.g. "203")  
    actual_room: Optional[str] = Field(default=None)  # Room actually occupied (e.g. "303")
    
    # Revenue attribution
    revenue_attribution: str = Field(default="actual_room")  # "booked_room" | "actual_room" | "split"
    
    # Change tracking
    change_reason: Optional[str] = Field(default=None)  # Why room was changed
    changed_date: Optional[date] = Field(default=None)  # When room change happened
    changed_by: Optional[str] = Field(default=None)  # Who made the change
    
    # Metadata
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            date: lambda d: d.isoformat()
        }
# ============ /ROOM ASSIGNMENT MODELS ============
