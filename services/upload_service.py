"""
Upload Service - CSV Processing and Data Import
=============================================

Handles:
- CSV file processing and validation
- Airbnb reservations data normalization
- Building/Property auto-creation and upsert
- Booking data upsert with conflict resolution
- Batch processing with progress tracking
"""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from fastapi import UploadFile
from sqlmodel import func, select

from models import Booking, Building, Channel, Property
from utils import (
    building_code_from_name,
    parse_building_and_unit,
    parse_date_mixed,
    parse_vnd,
    pick,
    unit_short_from_unit_number_auto,
)

from .base import BaseService


class UploadService(BaseService):
    """CSV upload and data processing service with user context support"""

    def process_upload_files(
        self,
        files: List[UploadFile],
        room_mapping_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process multiple uploaded CSV files with comprehensive validation

        Args:
            files: List of uploaded CSV files
            room_mapping_data: Optional room mapping configuration from frontend
                Expected format: {
                    "property_id": selected_property_id,
                    "mappings": {"airbnb_room_name": "target_property_name", ...}
                }

        Returns:
            Summary with inserted/updated counts, errors, processing time
        """
        started_all = datetime.utcnow()
        summaries = []
        total_inserted = 0
        total_updated = 0

        try:
            # Check permissions if user context available
            if self.current_user:
                if not self.check_permission("upload_csv"):
                    return self.error_response(
                        "Insufficient permissions to upload CSV files", 403
                    )

            # Apply room mapping if provided
            if room_mapping_data:
                from utils import update_room_mapping

                update_room_mapping(room_mapping_data)

            # Get or create default Airbnb channel
            airbnb_channel = self._get_or_create_airbnb_channel()

            # Process each file
            for upload_file in files:
                file_summary = self._process_single_file(
                    upload_file, airbnb_channel, room_mapping_data
                )
                summaries.append(file_summary)

                if file_summary.get("success"):
                    total_inserted += file_summary.get("rows_inserted", 0)
                    total_updated += file_summary.get("rows_updated", 0)

            # Commit all changes
            self.session.commit()

            processing_time = (datetime.utcnow() - started_all).total_seconds()

            self.log_activity(
                "process_upload_files",
                {
                    "total_files": len(files),
                    "total_inserted": total_inserted,
                    "total_updated": total_updated,
                    "processing_time_seconds": processing_time,
                },
            )

            return self.success_response(
                "Files processed successfully",
                {
                    "summaries": summaries,
                    "totals": {
                        "inserted": total_inserted,
                        "updated": total_updated,
                        "processing_time": processing_time,
                    },
                },
            )

        except Exception as e:
            self.session.rollback()
            return self.error_response(f"Failed to process upload files: {str(e)}", 500)

    def _process_single_file(
        self,
        upload_file: UploadFile,
        airbnb_channel: Channel,
        room_mapping_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a single CSV file and return summary"""
        filename = upload_file.filename or "uploaded.csv"
        rows_inserted = 0
        rows_updated = 0
        errors = []

        try:
            # Read and parse CSV
            content = upload_file.file.read()
            df = pd.read_csv(io.BytesIO(content))

            # Validate required columns
            validation_result = self._validate_csv_structure(df)
            if not validation_result["valid"]:
                return {
                    "filename": filename,
                    "success": False,
                    "error": validation_result["error"],
                    "rows_inserted": 0,
                    "rows_updated": 0,
                }

            # Process each row
            for index, row in df.iterrows():
                try:
                    row_result = self._process_csv_row(
                        row, df, airbnb_channel, room_mapping_data
                    )
                    if row_result["action"] == "inserted":
                        rows_inserted += 1
                    elif row_result["action"] == "updated":
                        rows_updated += 1

                except Exception as row_error:
                    errors.append({"row": index + 1, "error": str(row_error)})
                    continue

            return {
                "filename": filename,
                "success": True,
                "rows_inserted": rows_inserted,
                "rows_updated": rows_updated,
                "errors": errors,
                "total_rows": len(df),
            }

        except Exception as e:
            return {
                "filename": filename,
                "success": False,
                "error": f"Failed to process file: {str(e)}",
                "rows_inserted": 0,
                "rows_updated": 0,
            }

    def _validate_csv_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate CSV has required columns using utils.py mapping"""
        required_logical_columns = ["confirmation_code", "start_date", "end_date"]

        missing_columns = []
        for logical_col in required_logical_columns:
            if not pick(df, logical_col):
                missing_columns.append(logical_col)

        if missing_columns:
            return {
                "valid": False,
                "error": f"Missing required columns: {', '.join(missing_columns)}",
            }

        return {"valid": True}

    def _process_csv_row(
        self,
        row: pd.Series,
        df: pd.DataFrame,
        airbnb_channel: Channel,
        room_mapping_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process single CSV row into booking data"""

        # Extract and validate confirmation code
        cc_col = pick(df, "confirmation_code")
        if not cc_col:
            raise ValueError("No confirmation code column found")

        confirmation_code = str(row.get(cc_col, "")).strip()
        if not confirmation_code:
            raise ValueError("Empty confirmation code")

        # Extract all booking data
        booking_data = self._extract_booking_data(row, df, room_mapping_data)

        # Process building and property
        building, property_obj = self._process_building_and_property(booking_data)

        # Upsert booking
        action = self._upsert_booking(
            confirmation_code, booking_data, property_obj, airbnb_channel
        )

        return {"action": action, "confirmation_code": confirmation_code}

    def _extract_booking_data(
        self,
        row: pd.Series,
        df: pd.DataFrame,
        room_mapping_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Extract all booking fields from CSV row using utils.py mappings and apply room mapping"""

        # Status and guest info
        status_col = pick(df, "status")
        status = str(row.get(status_col, "")).strip() if status_col else None

        gname_col = pick(df, "guest_name")
        guest_name = str(row.get(gname_col, "")).strip() if gname_col else None

        gcontact_col = pick(df, "guest_contact")
        guest_contact = str(row.get(gcontact_col, "")).strip() if gcontact_col else None

        # Dates
        st_col = pick(df, "start_date")
        en_col = pick(df, "end_date")
        bk_col = pick(df, "booking_date")

        start_date = parse_date_mixed(row.get(st_col)) if st_col else None
        end_date = parse_date_mixed(row.get(en_col)) if en_col else None
        booking_date = parse_date_mixed(row.get(bk_col)) if bk_col else None

        # Calculate nights
        nights_col = pick(df, "num_nights")
        num_nights = row.get(nights_col) if nights_col else None
        try:
            num_nights = int(num_nights) if pd.notna(num_nights) else None
        except Exception:
            num_nights = None

        # Auto-calculate if missing but have dates
        if start_date and end_date:
            calc_nights = (end_date - start_date).days
            if calc_nights > 0:
                num_nights = int(calc_nights)

        # Guest counts
        ad_col = pick(df, "num_adults")
        ch_col = pick(df, "num_children")
        inf_col = pick(df, "num_infants")

        num_adults = (
            int(row.get(ad_col)) if ad_col and pd.notna(row.get(ad_col)) else None
        )
        num_children = (
            int(row.get(ch_col)) if ch_col and pd.notna(row.get(ch_col)) else None
        )
        num_infants = (
            int(row.get(inf_col)) if inf_col and pd.notna(row.get(inf_col)) else None
        )

        # Listing and income
        lst_col = pick(df, "listing")
        listing = str(row.get(lst_col, "")).strip() if lst_col else None

        # Apply room mapping if available
        if room_mapping_data and listing:
            from utils import apply_room_mapping

            listing = apply_room_mapping(listing, room_mapping_data)

        inc_col = pick(df, "income")
        income_vnd = parse_vnd(row.get(inc_col)) if inc_col else None

        return {
            "status": status,
            "guest_name": guest_name,
            "guest_contact": guest_contact,
            "start_date": start_date,
            "end_date": end_date,
            "booking_date": booking_date,
            "num_nights": num_nights,
            "num_adults": num_adults,
            "num_children": num_children,
            "num_infants": num_infants,
            "listing": listing,
            "income_vnd": income_vnd,
        }

    def _process_building_and_property(
        self, booking_data: Dict
    ) -> Tuple[Optional[Building], Optional[Property]]:
        """Process building and property creation/update"""
        listing = booking_data.get("listing")
        if not listing:
            return None, None

        # Parse building and unit information
        building_name, unit_number = parse_building_and_unit(listing)
        building_code = (
            building_code_from_name(building_name) if building_name else None
        )
        unit_short = (
            unit_short_from_unit_number_auto(unit_number) if unit_number else None
        )
        property_short = (
            f"{building_code}-{unit_short}" if (building_code and unit_short) else None
        )

        # Upsert building
        building = None
        if building_name:
            building = self.session.exec(
                select(Building).where(Building.building_name == building_name)
            ).first()

            if not building:
                building = Building(
                    building_name=building_name, building_code=building_code
                )
                self.session.add(building)
                self.session.commit()
                self.session.refresh(building)

        # Upsert property
        property_obj = None
        if listing:
            # Try finding by airbnb_name first
            property_obj = self.session.exec(
                select(Property).where(Property.airbnb_name == listing)
            ).first()

            # If not found, try by property_name
            if not property_obj:
                property_obj = self.session.exec(
                    select(Property).where(Property.property_name == listing)
                ).first()

            # Create new property if not found
            if not property_obj:
                property_obj = Property(
                    property_name=property_short or listing,
                    airbnb_name=listing,
                    building_id=building.id if building else None,
                    building_name=building_name,
                    building_code=building_code,
                    unit_number=unit_number,
                    unit_short=unit_short,
                    property_short=property_short,
                )
                self.session.add(property_obj)
                self.session.commit()
                self.session.refresh(property_obj)
            else:
                # Update existing property with missing info
                updated = False
                if (not property_obj.building_id) and building:
                    property_obj.building_id = building.id
                    updated = True
                if (not property_obj.building_name) and building_name:
                    property_obj.building_name = building_name
                    updated = True
                if (not property_obj.building_code) and building_code:
                    property_obj.building_code = building_code
                    updated = True
                if (not property_obj.unit_number) and unit_number:
                    property_obj.unit_number = unit_number
                    updated = True
                if (not property_obj.unit_short) and unit_short:
                    property_obj.unit_short = unit_short
                    updated = True
                if (not property_obj.property_short) and property_short:
                    property_obj.property_short = property_short
                    updated = True

                if updated:
                    self.session.add(property_obj)
                    self.session.commit()

        return building, property_obj

    def _upsert_booking(
        self,
        confirmation_code: str,
        booking_data: Dict,
        property_obj: Optional[Property],
        airbnb_channel: Channel,
    ) -> str:
        """Upsert booking record, return 'inserted' or 'updated'"""

        existing = self.session.exec(
            select(Booking).where(Booking.confirmation_code == confirmation_code)
        ).first()

        if existing:
            # Update existing booking
            existing.property_id = (
                property_obj.id if property_obj else existing.property_id
            )
            existing.channel_id = (
                airbnb_channel.id if airbnb_channel else existing.channel_id
            )
            existing.start_date = booking_data["start_date"] or existing.start_date
            existing.end_date = booking_data["end_date"] or existing.end_date

            if booking_data["num_nights"] is not None:
                existing.num_nights = booking_data["num_nights"]
            if booking_data["num_adults"] is not None:
                existing.num_adults = booking_data["num_adults"]
            if booking_data["num_children"] is not None:
                existing.num_children = booking_data["num_children"]
            if booking_data["num_infants"] is not None:
                existing.num_infants = booking_data["num_infants"]

            existing.booking_date = (
                booking_data["booking_date"] or existing.booking_date
            )
            existing.status = booking_data["status"] or existing.status

            if booking_data["income_vnd"] is not None:
                existing.total_payout_vnd = booking_data["income_vnd"]

            existing.guest_name = booking_data["guest_name"] or existing.guest_name
            existing.guest_contact = (
                booking_data["guest_contact"] or existing.guest_contact
            )
            existing.listing_raw = booking_data["listing"] or existing.listing_raw

            self.session.add(existing)
            return "updated"

        else:
            # Create new booking
            new_booking = Booking(
                confirmation_code=confirmation_code,
                property_id=property_obj.id if property_obj else None,
                channel_id=airbnb_channel.id if airbnb_channel else None,
                start_date=booking_data["start_date"],
                end_date=booking_data["end_date"],
                num_nights=booking_data["num_nights"],
                num_adults=booking_data["num_adults"],
                num_children=booking_data["num_children"],
                num_infants=booking_data["num_infants"],
                booking_date=booking_data["booking_date"],
                status=booking_data["status"],
                total_payout_vnd=booking_data["income_vnd"],
                guest_name=booking_data["guest_name"],
                guest_contact=booking_data["guest_contact"],
                listing_raw=booking_data["listing"],
            )

            self.session.add(new_booking)
            return "inserted"

    def _get_or_create_airbnb_channel(self) -> Channel:
        """Get or create default Airbnb channel"""
        airbnb = self.session.exec(
            select(Channel).where(Channel.channel_name == "Airbnb")
        ).first()

        if not airbnb:
            airbnb = Channel(channel_name="Airbnb")
            self.session.add(airbnb)
            self.session.commit()
            self.session.refresh(airbnb)

        return airbnb

    # ==================
    # UTILITY METHODS
    # ==================

    def validate_csv_preview(self, upload_file: UploadFile) -> Dict[str, Any]:
        """Preview CSV structure without processing data"""
        try:
            content = upload_file.file.read()
            df = pd.read_csv(io.BytesIO(content), nrows=5)  # Preview first 5 rows

            # Reset file pointer for potential reuse
            upload_file.file.seek(0)

            # Analyze column mappings
            column_analysis = {}
            logical_columns = [
                "confirmation_code",
                "start_date",
                "end_date",
                "listing",
                "income",
                "guest_name",
            ]

            for logical_col in logical_columns:
                mapped_col = pick(df, logical_col)
                column_analysis[logical_col] = {
                    "found": bool(mapped_col),
                    "mapped_to": mapped_col,
                    "sample_values": df[mapped_col].head(3).tolist()
                    if mapped_col
                    else [],
                }

            return self.success_response(
                "CSV preview generated",
                {
                    "total_rows": len(df),
                    "columns": df.columns.tolist(),
                    "column_mappings": column_analysis,
                    "sample_data": df.head(3).to_dict("records"),
                },
            )

        except Exception as e:
            return self.error_response(f"Failed to preview CSV: {str(e)}", 400)

    def get_upload_statistics(self) -> Dict[str, Any]:
        """Get upload/processing statistics"""
        try:
            # Count total bookings
            total_bookings = self.session.exec(select(func.count(Booking.id))).one()

            # Count by channel
            channel_stats = self.session.exec(
                select(Channel.channel_name, func.count(Booking.id))
                .join(Booking, Channel.id == Booking.channel_id, isouter=True)
                .group_by(Channel.channel_name)
            ).all()

            return self.success_response(
                "Upload statistics retrieved",
                {
                    "total_bookings": total_bookings,
                    "by_channel": [
                        {"channel": stat[0], "count": stat[1]} for stat in channel_stats
                    ],
                },
            )

        except Exception as e:
            return self.error_response(
                f"Failed to get upload statistics: {str(e)}", 500
            )
