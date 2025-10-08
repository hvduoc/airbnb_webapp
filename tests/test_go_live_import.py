"""
Unit Tests for Go-Live Import Pipeline
Tests mapper, validation, and idempotency functionality
"""

import json
import sys
import tempfile
import unittest
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd

# Add parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from csv_mapper import CSVMapper, ImportPipeline


class TestCSVMapper(unittest.TestCase):
    """Test CSV mapping functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary mapping file for testing
        self.test_mapping = {
            "offline_to_airbnb": {
                "Tên khách": "guest_name",
                "Số đêm": "num_nights",
                "Ngày checkin": "start_date",
                "Ngày checkout": "end_date",
                "Số tiền": "total_payout_vnd",
                "Ghi chú": "notes",
                "Mã đặt": "external_ref",
            },
            "date_formats": ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"],
            "amount_formats": {
                "remove_chars": [".", ",", "đ", "VND", " "],
                "multipliers": {"k": 1000, "tr": 1000000, "triệu": 1000000},
            },
            "validation_rules": {
                "adr_range": [10000, 10000000],
                "nights_range": [1, 365],
                "required_fields": ["guest_name", "start_date", "total_payout_vnd"],
            },
        }

        # Create temporary mapping file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(self.test_mapping, self.temp_file)
        self.temp_file.close()

        self.mapper = CSVMapper(self.temp_file.name)

    def tearDown(self):
        """Clean up test fixtures"""
        import os

        os.unlink(self.temp_file.name)

    def test_map_offline_row_basic(self):
        """Test basic offline row mapping"""
        offline_row = {
            "Tên khách": "Nguyễn Văn A",
            "Số đêm": "3",
            "Ngày checkin": "15/10/2025",
            "Ngày checkout": "18/10/2025",
            "Số tiền": "1.500.000đ",
            "Ghi chú": "Khách VIP",
            "Mã đặt": "FB001",
        }

        mapped = self.mapper.map_row(offline_row, "offline")

        self.assertEqual(mapped["guest_name"], "Nguyễn Văn A")
        self.assertEqual(mapped["num_nights"], 3)
        self.assertEqual(mapped["start_date"], date(2025, 10, 15))
        self.assertEqual(mapped["end_date"], date(2025, 10, 18))
        self.assertEqual(mapped["total_payout_vnd"], 1500000)
        self.assertEqual(mapped["notes"], "Khách VIP")
        self.assertEqual(mapped["external_ref"], "FB001")
        self.assertEqual(mapped["status"], "xác nhận")

    def test_parse_date_multiple_formats(self):
        """Test date parsing with different formats"""
        test_cases = [
            ("15/10/2025", date(2025, 10, 15)),
            ("2025-10-15", date(2025, 10, 15)),
            ("15-10-2025", date(2025, 10, 15)),
        ]

        for date_str, expected in test_cases:
            result = self.mapper._parse_date(date_str)
            self.assertEqual(result, expected, f"Failed to parse {date_str}")

    def test_parse_amount_with_multipliers(self):
        """Test amount parsing with Vietnamese multipliers"""
        test_cases = [
            ("1.500.000đ", 1500000),
            ("1500k", 1500000),  # 1500 thousand = 1.5 million
            ("500k", 500000),
            ("2 triệu", 2000000),
            ("1500000", 1500000),
        ]

        for amount_str, expected in test_cases:
            result = self.mapper._parse_amount(amount_str)
            self.assertEqual(
                result,
                expected,
                f"Failed to parse {amount_str}: got {result}, expected {expected}",
            )

    def test_validate_row_success(self):
        """Test successful row validation"""
        valid_row = {
            "guest_name": "Nguyễn Văn A",
            "start_date": date(2025, 10, 15),
            "end_date": date(2025, 10, 18),
            "num_nights": 3,
            "total_payout_vnd": 1500000,
        }

        is_valid, error = self.mapper.validate_row(valid_row)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_row_missing_required_field(self):
        """Test validation failure with missing required field"""
        invalid_row = {
            "start_date": date(2025, 10, 15),
            "total_payout_vnd": 1500000,
            # Missing guest_name
        }

        is_valid, error = self.mapper.validate_row(invalid_row)
        self.assertFalse(is_valid)
        self.assertIn("guest_name", error)

    def test_validate_row_amount_out_of_range(self):
        """Test validation failure with amount out of range"""
        invalid_row = {
            "guest_name": "Nguyễn Văn A",
            "start_date": date(2025, 10, 15),
            "total_payout_vnd": 5000,  # Too low
        }

        is_valid, error = self.mapper.validate_row(invalid_row)
        self.assertFalse(is_valid)
        self.assertIn("outside reasonable range", error)

    def test_generate_row_hash_consistent(self):
        """Test that row hash generation is consistent"""
        row1 = {
            "guest_name": "Nguyễn Văn A",
            "start_date": date(2025, 10, 15),
            "total_payout_vnd": 1500000,
        }

        row2 = {
            "guest_name": "Nguyễn Văn A",
            "start_date": date(2025, 10, 15),
            "total_payout_vnd": 1500000,
            "notes": "Additional notes",  # Extra field shouldn't affect hash
        }

        hash1 = self.mapper.generate_row_hash(row1)
        hash2 = self.mapper.generate_row_hash(row2)

        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA-256 hex string


class TestImportPipeline(unittest.TestCase):
    """Test import pipeline functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = ImportPipeline()

    def test_process_csv_valid_data(self):
        """Test processing CSV with valid data"""
        csv_data = """Tên khách,Số đêm,Ngày checkin,Ngày checkout,Số tiền
Nguyễn Văn A,3,15/10/2025,18/10/2025,1.500.000đ
Trần Thị B,2,20/10/2025,22/10/2025,1.200.000đ"""

        df = pd.read_csv(StringIO(csv_data))
        valid_rows, ingestion_id = self.pipeline.process_csv(df, "offline", "facebook")

        self.assertEqual(len(valid_rows), 2)
        self.assertIsNotNone(ingestion_id)
        self.assertEqual(self.pipeline.stats["valid"], 2)
        self.assertEqual(self.pipeline.stats["invalid"], 0)

        # Check that all rows have required metadata
        for row in valid_rows:
            self.assertEqual(row["source"], "offline")
            self.assertEqual(row["channel"], "facebook")
            self.assertEqual(row["ingestion_id"], ingestion_id)
            self.assertIsNotNone(row["row_hash"])

    def test_process_csv_invalid_data(self):
        """Test processing CSV with invalid data"""
        csv_data = """Tên khách,Số đêm,Ngày checkin,Ngày checkout,Số tiền
,3,15/10/2025,18/10/2025,1.500.000đ
Trần Thị B,2,invalid-date,22/10/2025,1.200.000đ
Valid Guest,1,15/10/2025,16/10/2025,1.000.000đ"""

        df = pd.read_csv(StringIO(csv_data))
        valid_rows, ingestion_id = self.pipeline.process_csv(df, "offline", "facebook")

        # Note: Only the third row should be valid (has guest name, valid dates, valid amount)
        # First row: missing guest name
        # Second row: invalid date format
        self.assertEqual(len(valid_rows), 1)  # Only one valid row
        self.assertGreaterEqual(
            self.pipeline.stats["invalid"], 1
        )  # At least one invalid

    def test_process_csv_duplicate_detection(self):
        """Test duplicate detection within single batch"""
        csv_data = """Tên khách,Số đêm,Ngày checkin,Ngày checkout,Số tiền
Nguyễn Văn A,3,15/10/2025,18/10/2025,1.500.000đ
Nguyễn Văn A,3,15/10/2025,18/10/2025,1.500.000đ"""

        df = pd.read_csv(StringIO(csv_data))
        valid_rows, ingestion_id = self.pipeline.process_csv(df, "offline", "facebook")

        self.assertEqual(len(valid_rows), 1)  # Duplicate should be filtered
        self.assertEqual(self.pipeline.stats["duplicates"], 1)

    def test_get_processing_summary(self):
        """Test processing summary generation"""
        # Process some test data first
        csv_data = """Tên khách,Số đêm,Ngày checkin,Ngày checkout,Số tiền
Nguyễn Văn A,3,15/10/2025,18/10/2025,1.500.000đ
Valid Guest,2,20/10/2025,22/10/2025,1.200.000đ"""

        df = pd.read_csv(StringIO(csv_data))
        self.pipeline.process_csv(df, "offline", "facebook")

        summary = self.pipeline.get_processing_summary()

        self.assertEqual(summary["total_rows"], 2)
        self.assertEqual(summary["valid_rows"], 2)  # Both rows should be valid now
        self.assertGreaterEqual(summary["success_rate"], 50.0)


class TestAirbnbCSVMapping(unittest.TestCase):
    """Test Airbnb CSV mapping functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mapper = CSVMapper()

    def test_map_airbnb_row(self):
        """Test mapping standard Airbnb CSV row"""
        airbnb_row = {
            "Mã xác nhận": "ABC123",
            "Nhà/phòng cho thuê": "Avalon 5.3 - OceanSight",
            "Tên khách": "John Doe",
            "Email, Số điện thoại": "john@example.com, +84123456789",
            "Ngày bắt đầu": "15/10/2025",
            "Ngày kết thúc": "18/10/2025",
            "# đêm": "3",
            "Thu nhập": "1.500.000",  # Remove special characters for test
            "Trạng thái đặt phòng": "Confirmed",
        }

        mapped = self.mapper.map_row(airbnb_row, "airbnb")

        self.assertEqual(mapped["confirmation_code"], "ABC123")
        self.assertEqual(mapped["listing_raw"], "Avalon 5.3 - OceanSight")
        self.assertEqual(mapped["guest_name"], "John Doe")
        self.assertEqual(mapped["guest_contact"], "john@example.com, +84123456789")
        self.assertEqual(mapped["start_date"], date(2025, 10, 15))
        self.assertEqual(mapped["end_date"], date(2025, 10, 18))
        self.assertEqual(mapped["num_nights"], 3)
        self.assertEqual(mapped["total_payout_vnd"], 1500000)
        self.assertEqual(mapped["status"], "Confirmed")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
