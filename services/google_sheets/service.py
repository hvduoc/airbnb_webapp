"""
Google Sheets Service for Payment Ledger
Handles all interactions with Google Sheets API for payment tracking
"""

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    gspread = None
    Credentials = None

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import GoogleSheetsConfig

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Service for managing Google Sheets operations"""
    
    def __init__(self):
        self.config = GoogleSheetsConfig()
        self.client = None
        self.spreadsheet = None
        self._executor = ThreadPoolExecutor(max_workers=3)
        
    async def initialize(self):
        """Initialize Google Sheets client and spreadsheet"""
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.warning("Google Sheets API not available - running in demo mode")
            return
            
        try:
            # Validate configuration
            self.config.validate_config()
            
            # Setup credentials
            credentials = Credentials.from_service_account_file(
                self.config.SERVICE_ACCOUNT_FILE,
                scopes=self.config.SCOPES
            )
            
            # Initialize client
            def _init_client():
                client = gspread.authorize(credentials)
                return client.open_by_key(self.config.SPREADSHEET_ID)
            
            # Run in thread pool to avoid blocking
            self.spreadsheet = await asyncio.get_event_loop().run_in_executor(
                self._executor, _init_client
            )
            
            # Initialize sheets if they don't exist
            await self._ensure_sheets_exist()
            
            logger.info("Google Sheets service initialized successfully")
            
        except Exception as e:
            logger.warning(f"Google Sheets service unavailable, running in demo mode: {e}")
            self.spreadsheet = None
    
    async def _ensure_sheets_exist(self):
        """Ensure required sheets exist with proper headers"""
        try:
            def _create_sheets():
                existing_sheets = [sheet.title for sheet in self.spreadsheet.worksheets()]
                
                # Create Payments sheet
                if self.config.PAYMENTS_SHEET not in existing_sheets:
                    sheet = self.spreadsheet.add_worksheet(
                        title=self.config.PAYMENTS_SHEET,
                        rows=1000,
                        cols=len(self.config.PAYMENT_HEADERS)
                    )
                    sheet.insert_row(self.config.PAYMENT_HEADERS, 1)
                
                # Create Cashflow sheet  
                if self.config.CASHFLOW_SHEET not in existing_sheets:
                    sheet = self.spreadsheet.add_worksheet(
                        title=self.config.CASHFLOW_SHEET,
                        rows=1000, 
                        cols=len(self.config.CASHFLOW_HEADERS)
                    )
                    sheet.insert_row(self.config.CASHFLOW_HEADERS, 1)
                    
                # Create Dashboard Data sheet
                if self.config.DASHBOARD_SHEET not in existing_sheets:
                    sheet = self.spreadsheet.add_worksheet(
                        title=self.config.DASHBOARD_SHEET,
                        rows=100,
                        cols=10
                    )
                    sheet.insert_row([
                        "Metric", "Value", "Date", "Details"
                    ], 1)
            
            await asyncio.get_event_loop().run_in_executor(
                self._executor, _create_sheets
            )
            
        except Exception as e:
            logger.error(f"Failed to ensure sheets exist: {e}")
            raise
    
    async def add_payment(self, payment_data: Dict[str, Any]) -> bool:
        """Add a new payment record to the Payments sheet"""
        if not GOOGLE_SHEETS_AVAILABLE or not self.spreadsheet:
            logger.info(f"Demo mode: Payment recorded - {payment_data.get('booking_id')}")
            return True
            
        try:
            def _add_payment():
                sheet = self.spreadsheet.worksheet(self.config.PAYMENTS_SHEET)
                
                # Prepare row data
                row_data = [
                    payment_data.get("timestamp", datetime.now().isoformat()),
                    payment_data.get("booking_id", ""),
                    payment_data.get("guest_name", ""),
                    payment_data.get("amount_due", 0),
                    payment_data.get("amount_collected", 0),
                    payment_data.get("payment_method", "cash"),
                    payment_data.get("collected_by", ""),
                    payment_data.get("transaction_id", ""),
                    payment_data.get("notes", ""),
                    payment_data.get("status", "completed")
                ]
                
                # Add row to sheet
                sheet.append_row(row_data)
                return True
            
            result = await asyncio.get_event_loop().run_in_executor(
                self._executor, _add_payment
            )
            
            logger.info(f"Payment added successfully: {payment_data.get('booking_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add payment: {e}")
            return False
    
    async def add_cashflow(self, cashflow_data: Dict[str, Any]) -> bool:
        """Add a cash handover record to the Cashflow sheet"""
        if not GOOGLE_SHEETS_AVAILABLE or not self.spreadsheet:
            logger.info(f"Demo mode: Cashflow recorded - {cashflow_data.get('transaction_type')}")
            return True
            
        try:
            def _add_cashflow():
                sheet = self.spreadsheet.worksheet(self.config.CASHFLOW_SHEET)
                
                # Prepare row data
                row_data = [
                    cashflow_data.get("timestamp", datetime.now().isoformat()),
                    cashflow_data.get("transaction_type", "handover"),
                    cashflow_data.get("from_person", ""),
                    cashflow_data.get("to_person", ""),
                    cashflow_data.get("amount", 0),
                    cashflow_data.get("cash_balance", 0),
                    cashflow_data.get("description", ""),
                    cashflow_data.get("approved_by", ""),
                    cashflow_data.get("status", "completed")
                ]
                
                # Add row to sheet
                sheet.append_row(row_data)
                return True
            
            result = await asyncio.get_event_loop().run_in_executor(
                self._executor, _add_cashflow
            )
            
            logger.info(f"Cashflow added successfully: {cashflow_data.get('transaction_type')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add cashflow: {e}")
            return False
    
    async def get_payments(self, 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          collected_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve payment records with optional filtering"""
        if not GOOGLE_SHEETS_AVAILABLE or not self.spreadsheet:
            # Return demo data
            return [
                {
                    "Timestamp": "2025-09-30T10:00:00",
                    "Booking ID": "BK001",
                    "Guest Name": "John Doe",
                    "Amount Due (VND)": 1000000,
                    "Amount Collected (VND)": 1000000,
                    "Payment Method": "cash",
                    "Collected By": "assistant",
                    "Transaction ID": "",
                    "Notes": "Demo payment record",
                    "Status": "completed"
                }
            ]
            
        try:
            def _get_payments():
                sheet = self.spreadsheet.worksheet(self.config.PAYMENTS_SHEET)
                records = sheet.get_all_records()
                
                # Apply filters
                filtered_records = []
                for record in records:
                    # Date filter
                    if start_date or end_date:
                        record_date = record.get("Timestamp", "")
                        if start_date and record_date < start_date:
                            continue
                        if end_date and record_date > end_date:
                            continue
                    
                    # Collector filter
                    if collected_by and record.get("Collected By", "") != collected_by:
                        continue
                        
                    filtered_records.append(record)
                
                return filtered_records
            
            records = await asyncio.get_event_loop().run_in_executor(
                self._executor, _get_payments
            )
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get payments: {e}")
            return []
    
    async def get_cashflow(self, 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve cashflow records"""
        if not GOOGLE_SHEETS_AVAILABLE or not self.spreadsheet:
            # Return demo data
            return [
                {
                    "Timestamp": "2025-09-30T09:00:00",
                    "Transaction Type": "handover",
                    "From Person": "assistant",
                    "To Person": "manager",
                    "Amount (VND)": 500000,
                    "Cash Balance": 500000,
                    "Description": "Daily cash handover",
                    "Approved By": "manager",
                    "Status": "completed"
                }
            ]
            
        try:
            def _get_cashflow():
                sheet = self.spreadsheet.worksheet(self.config.CASHFLOW_SHEET)
                records = sheet.get_all_records()
                
                # Apply date filter
                if start_date or end_date:
                    filtered_records = []
                    for record in records:
                        record_date = record.get("Timestamp", "")
                        if start_date and record_date < start_date:
                            continue
                        if end_date and record_date > end_date:
                            continue
                        filtered_records.append(record)
                    return filtered_records
                
                return records
            
            records = await asyncio.get_event_loop().run_in_executor(
                self._executor, _get_cashflow
            )
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get cashflow: {e}")
            return []
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get aggregated data for dashboard"""
        if not GOOGLE_SHEETS_AVAILABLE or not self.spreadsheet:
            # Return demo dashboard data
            return {
                "total_collected": 5000000,
                "total_due": 6000000,
                "collection_rate": 83.33,
                "cash_in": 3000000,
                "cash_out": 1000000,
                "cash_balance": 2000000,
                "total_payments": 10,
                "total_cashflow": 5,
                "last_updated": datetime.now().isoformat()
            }
            
        try:
            payments = await self.get_payments()
            cashflow = await self.get_cashflow()
            
            # Calculate metrics
            total_collected = sum(
                float(p.get("Amount Collected (VND)", 0)) for p in payments
            )
            
            total_due = sum(
                float(p.get("Amount Due (VND)", 0)) for p in payments  
            )
            
            cash_in = sum(
                float(c.get("Amount (VND)", 0)) 
                for c in cashflow 
                if c.get("Transaction Type") == "collection"
            )
            
            cash_out = sum(
                float(c.get("Amount (VND)", 0))
                for c in cashflow
                if c.get("Transaction Type") == "handover" 
            )
            
            return {
                "total_collected": total_collected,
                "total_due": total_due,
                "collection_rate": (total_collected / total_due * 100) if total_due > 0 else 0,
                "cash_in": cash_in,
                "cash_out": cash_out,
                "cash_balance": cash_in - cash_out,
                "total_payments": len(payments),
                "total_cashflow": len(cashflow),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {}

# Singleton instance
sheets_service = GoogleSheetsService()