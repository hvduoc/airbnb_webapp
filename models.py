# Phụ phí căn hộ
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

# ============ AUTHENTICATION MODELS ============
class User(SQLModel, table=True):
    """User model with authentication and role-based access"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    
    # Role-based access control
    role: str = Field(default="user")  # user, admin, manager, viewer
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    
    # Audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    
    # Property access control (JSON list of property IDs user can access)
    accessible_properties: Optional[str] = Field(default="[]")  # JSON string
    
class UserSession(SQLModel, table=True):
    """Track user sessions for security"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    token_jti: str = Field(unique=True)  # JWT ID for token tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_active: bool = Field(default=True)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# ============ EXISTING MODELS ============

class ExtraCharge(SQLModel, table=True):
    __tablename__ = "extra_charges"
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(index=True)
    charge_name: str
    charge_amount: int
    charge_month: str
    charge_note: Optional[str] = None
    created_at: Optional[str] = None
    category_id: Optional[int] = Field(default=None, index=True)  # Thêm trường category_id
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date, datetime

class Building(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    building_name: str
    building_code: Optional[str] = None
    address: Optional[str] = None
    # THÊM MỚI: Tọa độ cho tòa nhà
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)

class Property(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    building_id: Optional[int] = Field(default=None, foreign_key="building.id")
    building_name: Optional[str] = None
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
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_name: str

class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    confirmation_code: Optional[str] = None
    property_id: Optional[int] = Field(default=None, foreign_key="property.id")
    channel_id: Optional[int] = Field(default=None, foreign_key="channel.id")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    num_nights: Optional[int] = None
    num_adults: Optional[int] = None
    num_children: Optional[int] = None
    num_infants: Optional[int] = None
    booking_date: Optional[date] = None
    status: Optional[str] = None
    total_payout_vnd: Optional[int] = None
    guest_name: Optional[str] = None
    guest_contact: Optional[str] = None
    listing_raw: Optional[str] = None
    salesperson_id: Optional[int] = Field(default=None, foreign_key="salesperson.id")
    notes: Optional[str] = None    

class ImportLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    source: str = "upload-form"
    rows_inserted: int = 0
    rows_updated: int = 0
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

# ==== OPEX MODELS (append vào cuối models.py) ====
from sqlmodel import SQLModel, Field, Column, String
from typing import Optional
from datetime import datetime

class ExpenseCategory(SQLModel, table=True):
    __tablename__ = "expense_categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(default=None, foreign_key="expense_categories.id")
    is_fixed: int = 0

class Expense(SQLModel, table=True):
    __tablename__ = "expenses"
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str
    month: str = Field(sa_column=Column(String, index=True))
    category_id: int = Field(foreign_key="expense_categories.id")
    amount: int
    vendor: Optional[str] = None
    note: Optional[str] = None
    building_id: Optional[int] = None
    property_id: Optional[int] = None
    allocation_method: str = "direct"  # direct|per_property|per_available_night|per_occupied_night
    allocation_basis_note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RecurringExpense(SQLModel, table=True):
    __tablename__ = "recurring_expenses"
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="expense_categories.id")
    amount: int
    vendor: Optional[str] = None
    note: Optional[str] = None
    building_id: Optional[int] = None
    property_id: Optional[int] = None
    allocation_method: str = "per_property"
    start_month: str
    end_month: Optional[str] = None
    day_of_month: int = 1
    is_active: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ExpenseAllocation(SQLModel, table=True):
    __tablename__ = "expense_allocations"
    id: Optional[int] = Field(default=None, primary_key=True)
    expense_id: int = Field(foreign_key="expenses.id")
    property_id: int
    month: str
    allocated_amount: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
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
