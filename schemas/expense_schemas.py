"""
Pydantic Schemas for Expense API
================================

Validation schemas cho expense creation và filtering.
Vietnamese field descriptions và error messages.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, validator


class ExpenseCreateRequest(BaseModel):
    """Schema for creating new expense"""

    amount: int = Field(..., gt=0, description="Số tiền chi phí (VNĐ), phải > 0")
    category_id: int = Field(..., description="ID danh mục chi phí")
    property_id: Optional[int] = Field(None, description="ID bất động sản (optional)")
    building_id: Optional[int] = Field(None, description="ID tòa nhà (optional)")
    vendor: Optional[str] = Field(
        None, max_length=255, description="Nhà cung cấp/vendor"
    )
    note: Optional[str] = Field(None, max_length=500, description="Ghi chú thêm")
    date: str = Field(..., description="Ngày chi phí (YYYY-MM-DD)")
    allocation_method: str = Field(
        "direct", max_length=50, description="Phương thức phân bổ"
    )
    allocation_basis_note: Optional[str] = Field(
        None, max_length=500, description="Ghi chú phân bổ"
    )

    @validator("date")
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format"""
        try:
            parsed_date = date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @validator("amount")
    def validate_amount_reasonable(cls, v):
        """Validate amount is reasonable (not too large)"""
        if v > 1_000_000_000:  # 1 billion VND
            raise ValueError("Amount seems too large. Please verify.")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 500000,
                "category_id": 1,
                "property_id": 1,
                "vendor": "Công ty ABC",
                "note": "Chi phí sửa chữa điều hòa",
                "date": "2025-10-03",
                "allocation_method": "direct",
            }
        }


class ExpenseListRequest(BaseModel):
    """Schema for expense list filtering"""

    start_date: Optional[date] = Field(None, description="Từ ngày (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="Đến ngày (YYYY-MM-DD)")
    category_id: Optional[int] = Field(None, description="Lọc theo danh mục")
    property_id: Optional[int] = Field(None, description="Lọc theo bất động sản")
    vendor: Optional[str] = Field(
        None, description="Lọc theo vendor (tìm kiếm gần đúng)"
    )
    limit: int = Field(100, ge=1, le=1000, description="Số lượng kết quả tối đa")
    offset: int = Field(0, ge=0, description="Bỏ qua số kết quả đầu (pagination)")

    @validator("end_date")
    def validate_date_range(cls, v, values):
        """Validate end_date is after start_date"""
        if v and "start_date" in values and values["start_date"]:
            if v < values["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2025-10-01",
                "end_date": "2025-10-31",
                "category_id": 1,
                "limit": 50,
                "offset": 0,
            }
        }


class ExpenseSummaryRequest(BaseModel):
    """Schema for expense summary by property"""

    start_date: Optional[date] = Field(None, description="Từ ngày (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="Đến ngày (YYYY-MM-DD)")

    @validator("end_date")
    def validate_date_range(cls, v, values):
        """Validate end_date is after start_date"""
        if v and "start_date" in values and values["start_date"]:
            if v < values["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v

    class Config:
        json_schema_extra = {
            "example": {"start_date": "2025-10-01", "end_date": "2025-10-31"}
        }
