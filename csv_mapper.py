"""
Go-Live Import Pipeline - CSV Mapper and Validation
Handles both Airbnb official CSV and offline booking CSV files
"""

import hashlib
import json
import re
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from pydantic import BaseModel, validator

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class BookingValidationModel(BaseModel):
    """Pydantic model for booking validation"""
    guest_name: str
    start_date: date
    end_date: Optional[date] = None
    num_nights: Optional[int] = None
    total_payout_vnd: int
    guest_contact: Optional[str] = None
    listing_raw: Optional[str] = None
    notes: Optional[str] = None
    external_ref: Optional[str] = None
    
    @validator('total_payout_vnd')
    def validate_amount(cls, v):
        """Validate amount is within reasonable range"""
        if v < 10000 or v > 10000000:  # 10k to 10M VND
            raise ValueError(f"Amount {v:,} VND is outside reasonable range (10k-10M VND)")
        return v
    
    @validator('num_nights')
    def validate_nights(cls, v):
        """Validate number of nights"""
        if v is not None and (v < 1 or v > 365):
            raise ValueError(f"Number of nights {v} must be between 1-365")
        return v
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Validate date consistency"""
        start_date = values.get('start_date')
        if v and start_date and v <= start_date:
            raise ValueError("End date must be after start date")
        return v

class CSVMapper:
    """Mapper class to convert offline CSV to Airbnb format"""
    
    def __init__(self, mapping_file: str = "mapping.json"):
        """Initialize mapper with mapping configuration"""
        with open(mapping_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.mapping = self.config['offline_to_airbnb']
        self.date_formats = self.config['date_formats']
        self.amount_config = self.config['amount_formats']
        self.validation_rules = self.config['validation_rules']
    
    def map_row(self, row: Dict[str, Any], source: str = "offline") -> Dict[str, Any]:
        """
        Map a single row from offline CSV to Airbnb format
        
        Args:
            row: Dictionary representing CSV row
            source: Source type ("airbnb" or "offline")
            
        Returns:
            Mapped row dictionary
        """
        if source == "airbnb":
            return self._map_airbnb_row(row)
        else:
            return self._map_offline_row(row)
    
    def _map_airbnb_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Map Airbnb CSV row (minimal processing needed)"""
        mapped = {}
        
        # Standard Airbnb field mapping (from utils.py)
        airbnb_mapping = {
            "Mã xác nhận": "confirmation_code",
            "Nhà/phòng cho thuê": "listing_raw", 
            "Tên khách": "guest_name",
            "Email, Số điện thoại": "guest_contact",
            "Ngày bắt đầu": "start_date",
            "Ngày kết thúc": "end_date",
            "# đêm": "num_nights",
            "Thu nhập": "total_payout_vnd",
            "Trạng thái đặt phòng": "status"
        }
        
        for csv_key, db_field in airbnb_mapping.items():
            if csv_key in row and row[csv_key] is not None:
                if db_field in ['start_date', 'end_date']:
                    mapped[db_field] = self._parse_date(row[csv_key])
                elif db_field == 'total_payout_vnd':
                    mapped[db_field] = self._parse_amount(row[csv_key])
                elif db_field == 'num_nights':
                    mapped[db_field] = self._parse_int(row[csv_key])
                else:
                    mapped[db_field] = str(row[csv_key]).strip()
        
        return mapped
    
    def _map_offline_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Map offline CSV row to Airbnb format"""
        mapped = {}
        
        # Apply mapping rules
        for csv_key, db_field in self.mapping.items():
            if csv_key in row and row[csv_key] is not None:
                if db_field in ['start_date', 'end_date']:
                    mapped[db_field] = self._parse_date(row[csv_key])
                elif db_field == 'total_payout_vnd':
                    mapped[db_field] = self._parse_amount(row[csv_key])
                elif db_field == 'num_nights':
                    mapped[db_field] = self._parse_int(row[csv_key])
                else:
                    mapped[db_field] = str(row[csv_key]).strip()
        
        # Calculate missing fields
        if 'start_date' in mapped and 'end_date' in mapped:
            start = mapped['start_date']
            end = mapped['end_date']
            if isinstance(start, date) and isinstance(end, date):
                mapped['num_nights'] = (end - start).days
        
        # Set defaults
        mapped.setdefault('status', 'xác nhận')
        mapped.setdefault('booking_date', date.today())
        
        return mapped
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string with multiple format support"""
        if not date_str or pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _parse_amount(self, amount_str: str) -> int:
        """Parse amount string to integer VND"""
        if not amount_str or pd.isna(amount_str):
            return 0
        
        amount_str = str(amount_str).strip().lower()
        original_amount = amount_str
        
        # Handle multipliers first
        multiplier = 1
        for suffix, mult in self.amount_config['multipliers'].items():
            if amount_str.endswith(suffix.lower()):
                multiplier = mult
                amount_str = amount_str[:-len(suffix)].strip()
                break
        
        # If we have a multiplier, handle comma as decimal separator
        if multiplier > 1 and ',' in amount_str:
            amount_str = amount_str.replace(',', '.')
        elif ',' in amount_str and '.' in amount_str:
            # Both comma and dot present - assume dots are thousand separators, comma is decimal
            # e.g., "1.500,50" -> "1500.50"
            parts = amount_str.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                amount_str = f"{integer_part}.{decimal_part}"
        elif ',' in amount_str and multiplier == 1:
            # Just comma, no multiplier - treat as thousand separator
            amount_str = amount_str.replace(',', '')
        
        # Remove unwanted characters  
        for char in self.amount_config['remove_chars']:
            amount_str = amount_str.replace(char, '')
        
        try:
            amount = float(amount_str) * multiplier
            return int(amount)
        except ValueError:
            raise ValueError(f"Unable to parse amount: {original_amount}")
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer value"""
        if value is None or pd.isna(value):
            return None
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return None
    
    def validate_row(self, mapped_row: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate mapped row against business rules
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Required fields check
            for field in self.validation_rules['required_fields']:
                if field not in mapped_row or mapped_row[field] is None:
                    return False, f"Missing required field: {field}"
            
            # Use Pydantic for validation
            BookingValidationModel(**mapped_row)
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def generate_row_hash(self, mapped_row: Dict[str, Any]) -> str:
        """Generate unique hash for idempotency"""
        hash_data = f"{mapped_row.get('guest_name', '')}-{mapped_row.get('start_date', '')}-{mapped_row.get('total_payout_vnd', 0)}"
        return hashlib.sha256(hash_data.encode()).hexdigest()

class ImportPipeline:
    """Main import pipeline orchestrator"""
    
    def __init__(self):
        self.mapper = CSVMapper()
        self.errors = []
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'duplicates': 0
        }
    
    def process_csv(self, df: pd.DataFrame, source: str, channel: str) -> Tuple[List[Dict], str]:
        """
        Process entire CSV file
        
        Args:
            df: Pandas DataFrame of CSV data
            source: "airbnb" or "offline"
            channel: Specific channel like "facebook", "zalo", etc.
            
        Returns:
            (valid_rows, ingestion_id)
        """
        ingestion_id = str(uuid.uuid4())
        valid_rows = []
        seen_hashes = set()
        
        self.stats['total'] = len(df)
        
        for idx, row in df.iterrows():
            try:
                # Map row
                mapped_row = self.mapper.map_row(row.to_dict(), source)
                
                # Add import metadata
                mapped_row.update({
                    'source': source,
                    'channel': channel,
                    'ingestion_id': ingestion_id,
                    'imported_at': datetime.utcnow()
                })
                
                # Generate hash for idempotency
                row_hash = self.mapper.generate_row_hash(mapped_row)
                mapped_row['row_hash'] = row_hash
                
                # Check for duplicates in current batch
                if row_hash in seen_hashes:
                    self.stats['duplicates'] += 1
                    self._log_error(idx, row.to_dict(), "Duplicate row in current batch")
                    continue
                
                seen_hashes.add(row_hash)
                
                # Validate row
                is_valid, error_msg = self.mapper.validate_row(mapped_row)
                if not is_valid:
                    self.stats['invalid'] += 1
                    self._log_error(idx, row.to_dict(), error_msg)
                    continue
                
                valid_rows.append(mapped_row)
                self.stats['valid'] += 1
                
            except Exception as e:
                self.stats['invalid'] += 1
                self._log_error(idx, row.to_dict(), str(e))
        
        return valid_rows, ingestion_id
    
    def _log_error(self, row_idx: int, original_row: Dict, error_msg: str):
        """Log validation error"""
        self.errors.append({
            'row_index': row_idx,
            'original_data': original_row,
            'error_reason': error_msg,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def save_error_log(self, filename: str) -> Optional[str]:
        """Save errors to CSV file"""
        if not self.errors:
            return None
        
        error_df = pd.DataFrame(self.errors)
        error_file = f"errors_{filename}"
        error_df.to_csv(error_file, index=False, encoding='utf-8')
        return error_file
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing statistics summary"""
        return {
            'total_rows': self.stats['total'],
            'valid_rows': self.stats['valid'],
            'invalid_rows': self.stats['invalid'],
            'duplicate_rows': self.stats['duplicates'],
            'success_rate': round(self.stats['valid'] / max(self.stats['total'], 1) * 100, 2),
            'error_count': len(self.errors)
        }

# Example usage
if __name__ == "__main__":
    # Test mapper
    mapper = CSVMapper()
    
    # Test offline row
    offline_row = {
        "Tên khách": "Nguyễn Văn A",
        "Số đêm": "3",
        "Ngày checkin": "15/10/2025",
        "Ngày checkout": "18/10/2025", 
        "Số tiền": "1.500.000đ",
        "Ghi chú": "Khách VIP",
        "Mã đặt": "FB001"
    }
    
    mapped = mapper.map_row(offline_row, "offline")
    print("Mapped row:", mapped)
    
    is_valid, error = mapper.validate_row(mapped)
    print(f"Valid: {is_valid}, Error: {error}")