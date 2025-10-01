"""
Payment Ledger Models for Google Sheets Integration
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum

class PaymentMethod(str, Enum):
    """Available payment methods"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    AIRBNB_PAYOUT = "airbnb_payout"
    MOMO = "momo"
    ZALOPAY = "zalopay"
    VIETQR = "vietqr"

class PaymentStatus(str, Enum):
    """Payment status options"""
    PENDING = "pending"
    COMPLETED = "completed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"

class UserRole(str, Enum):
    """User roles for cash handling"""
    ASSISTANT = "assistant"
    MANAGER = "manager"
    OWNER = "owner"

class TransactionType(str, Enum):
    """Cash transaction types"""
    COLLECTION = "collection"
    HANDOVER = "handover"
    EXPENSE = "expense"
    ADJUSTMENT = "adjustment"

# ============ REQUEST/RESPONSE MODELS ============

class PaymentRequest(SQLModel):
    """Request model for adding a new payment"""
    booking_id: str
    guest_name: str
    amount_due: float
    amount_collected: float
    payment_method: PaymentMethod
    collected_by: str
    notes: Optional[str] = None
    transaction_id: Optional[str] = None

class PaymentResponse(SQLModel):
    """Response model for payment data"""
    timestamp: str
    booking_id: str
    guest_name: str
    amount_due: float
    amount_collected: float
    payment_method: str
    collected_by: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    status: str

class CashHandoverRequest(SQLModel):
    """Request model for cash handover"""
    from_person: str
    to_person: str
    amount: float
    description: str
    approved_by: Optional[str] = None

class CashHandoverResponse(SQLModel):
    """Response model for cash handover"""
    timestamp: str
    transaction_type: str
    from_person: str
    to_person: str
    amount: float
    cash_balance: float
    description: str
    approved_by: Optional[str] = None
    status: str

class DashboardData(SQLModel):
    """Dashboard metrics response"""
    total_collected: float
    total_due: float
    collection_rate: float
    cash_in: float
    cash_out: float
    cash_balance: float
    total_payments: int
    total_cashflow: int
    last_updated: str

class PaymentListRequest(SQLModel):
    """Request parameters for payment list filtering"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    collected_by: Optional[str] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0

class CashflowListRequest(SQLModel):
    """Request parameters for cashflow list filtering"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    transaction_type: Optional[str] = None
    person: Optional[str] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0

# ============ AUTHENTICATION MODELS ============

class PaymentUser(SQLModel):
    """User model for payment system authentication"""
    id: int
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    accessible_properties: List[str] = Field(default_factory=list)

class LoginRequest(SQLModel):
    """Login request model"""
    username: str
    password: str

class TokenResponse(SQLModel):
    """JWT token response"""
    access_token: str
    token_type: str
    expires_in: int
    user: PaymentUser

# ============ VALIDATION MODELS ============

class PaymentValidation(SQLModel):
    """Validation rules for payments"""
    min_amount: float = 0
    max_amount: float = 100_000_000  # 100M VND
    required_fields: List[str] = [
        "booking_id", "guest_name", "amount_due", 
        "amount_collected", "payment_method", "collected_by"
    ]
    
    @classmethod
    def validate_payment(cls, payment: PaymentRequest) -> List[str]:
        """Validate payment data and return list of errors"""
        errors = []
        
        # Check required fields
        for field in cls.required_fields:
            if not getattr(payment, field, None):
                errors.append(f"{field} is required")
        
        # Amount validation
        if payment.amount_collected < cls.min_amount:
            errors.append(f"Amount collected must be >= {cls.min_amount}")
        
        if payment.amount_collected > cls.max_amount:
            errors.append(f"Amount collected must be <= {cls.max_amount}")
        
        # Business logic validation
        if payment.amount_collected > payment.amount_due:
            errors.append("Amount collected cannot exceed amount due")
        
        return errors