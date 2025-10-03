"""
Service Layer Package - COMPLETE EXTRACTION
============================================

Business logic services for the Airbnb Revenue Management WebApp.

Services:
- BaseService: Foundation service with user context, permissions, audit trail hooks
- BookingService: Complete booking CRUD operations with user-aware filtering  
- PropertyService: Building and property management operations
- RevenueService: Monthly reports and analytics with comprehensive KPI calculations
- UploadService: CSV processing, data validation, file handling with batch processing
- SalespersonService: Sales team management, commission calculations, performance analytics

Architecture:
- User-aware patterns ready for authentication integration
- Permission checking built-in
- Audit trail hooks prepared  
- Database session management
- Standardized response formats
- Complete business logic separation from main.py
"""

from .base import BaseService
from .booking_service import BookingService
from .property_service import PropertyService
from .revenue_service import RevenueService
from .salesperson_service import SalespersonService
from .upload_service import UploadService

__all__ = [
    "BaseService",
    "BookingService", 
    "PropertyService",
    "RevenueService",
    "UploadService",
    "SalespersonService"
]