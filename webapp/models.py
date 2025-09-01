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