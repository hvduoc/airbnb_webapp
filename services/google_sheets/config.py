# Google Sheets API Configuration
import os
from typing import List

class GoogleSheetsConfig:
    """Configuration for Google Sheets API integration"""
    
    # Service Account Credentials
    SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/service-account.json")
    
    # Spreadsheet Configuration
    SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
    
    # Sheet Names
    PAYMENTS_SHEET = "Payments"
    CASHFLOW_SHEET = "Cashflow"
    DASHBOARD_SHEET = "Dashboard_Data"
    
    # API Scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    # Payment Headers
    PAYMENT_HEADERS = [
        "Timestamp",
        "Booking ID", 
        "Guest Name",
        "Amount Due (VND)",
        "Amount Collected (VND)",
        "Payment Method",
        "Collected By",
        "Transaction ID",
        "Notes",
        "Status"
    ]
    
    # Cashflow Headers
    CASHFLOW_HEADERS = [
        "Timestamp",
        "Transaction Type",  # Handover, Collection, Expense
        "From Person",
        "To Person", 
        "Amount (VND)",
        "Cash Balance",
        "Description",
        "Approved By",
        "Status"
    ]
    
    # Payment Methods
    PAYMENT_METHODS = [
        "cash",
        "bank_transfer",
        "airbnb_payout",
        "momo",
        "zalopay",
        "vietqr"
    ]
    
    # User Roles for Cash Handling
    CASH_ROLES = {
        "assistant": "Assistant",
        "manager": "Manager", 
        "owner": "Owner"
    }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate if all required configuration is present"""
        try:
            if not cls.SPREADSHEET_ID:
                raise ValueError("GOOGLE_SPREADSHEET_ID environment variable is required")
            
            if not os.path.exists(cls.SERVICE_ACCOUNT_FILE):
                raise ValueError(f"Service account file not found: {cls.SERVICE_ACCOUNT_FILE}")
                
            return True
        except Exception as e:
            # In demo mode, just log the issue but don't fail
            print(f"Google Sheets config issue (running in demo mode): {e}")
            return False