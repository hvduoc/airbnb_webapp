"""
Booking Service - Business logic for booking management
Extracted from main.py for better architecture and user-aware operations
"""

import uuid
from datetime import date, datetime
from typing import Dict, Optional

from sqlmodel import select

from models import Booking, Channel, Property, RoomAssignment, Salesperson
from services.base import BaseService


class BookingService(BaseService):
    """
    Service for managing Airbnb booking operations
    Includes CRUD operations, business logic, and user-aware filtering
    """

    def get_booking_list_data(
        self,
        property_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Get booking list with filtering support

        Args:
            property_id: Filter by property
            channel_id: Filter by channel
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            Dict with bookings and metadata
        """
        try:
            with self.get_session() as session:
                # Base query với user filtering if needed
                query = select(Booking)

                # Apply filters
                if property_id:
                    query = query.where(Booking.property_id == property_id)
                if channel_id:
                    query = query.where(Booking.channel_id == channel_id)
                if start_date:
                    query = query.where(Booking.start_date >= start_date)
                if end_date:
                    query = query.where(Booking.end_date <= end_date)

                # TODO: Add user filtering when audit system ready
                # user_filter = self.get_user_filter_clause(Booking, "created_by")
                # if user_filter is not None:
                #     query = query.where(user_filter)

                bookings = session.exec(query.order_by(Booking.start_date.desc())).all()

                # Get related data for filters
                properties = session.exec(
                    select(Property).order_by(Property.property_name)
                ).all()
                channels = session.exec(
                    select(Channel).order_by(Channel.channel_name)
                ).all()

                self.log_action("list", "booking", details={"count": len(bookings)})

                return self.format_success_response(
                    {
                        "bookings": bookings,
                        "properties": properties,
                        "channels": channels,
                        "filters": {
                            "property_id": property_id,
                            "channel_id": channel_id,
                            "start_date": start_date,
                            "end_date": end_date,
                        },
                    }
                )

        except Exception as e:
            return self.format_error_response(f"Error fetching bookings: {str(e)}")

    def get_booking_detail(self, booking_id: int) -> Dict:
        """
        Get single booking details

        Args:
            booking_id: Booking ID to retrieve

        Returns:
            Dict with booking data or error
        """
        try:
            booking = self.session.get(Booking, booking_id)

            if not booking:
                return {"success": False, "message": "Booking not found", "data": None}

            # TODO: Check user access when audit system ready
            # TODO: Add audit logging

            return {"success": True, "data": booking}

        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching booking: {str(e)}",
                "data": None,
            }

    def get_new_booking_form_data(
        self,
        channel: Optional[str] = None,
        channel_id: Optional[int] = None,
        offline: Optional[bool] = False,
    ) -> Dict:
        """
        Get data needed for new booking form

        Args:
            channel: Channel name for default selection
            channel_id: Channel ID for default selection
            offline: Whether to default to offline channel

        Returns:
            Dict with form data
        """
        self.require_permission("user")  # Users can create bookings

        try:
            with self.get_session() as session:
                properties = session.exec(
                    select(Property).order_by(Property.property_name)
                ).all()
                channels = session.exec(
                    select(Channel).order_by(Channel.channel_name)
                ).all()
                salespeople = session.exec(
                    select(Salesperson).where(Salesperson.is_active)
                ).all()

                # Determine default channel
                default_channel_id = None
                if channel_id:
                    default_channel_id = channel_id
                elif channel:
                    ch = session.exec(
                        select(Channel).where(Channel.channel_name.ilike(channel))
                    ).first()
                    default_channel_id = ch.id if ch else None
                elif offline:
                    ch = session.exec(
                        select(Channel).where(Channel.channel_name == "Offline")
                    ).first()
                    default_channel_id = ch.id if ch else None

                return self.format_success_response(
                    {
                        "properties": properties,
                        "channels": channels,
                        "salespeople": salespeople,
                        "default_channel_id": default_channel_id,
                    }
                )

        except Exception as e:
            return self.format_error_response(f"Error loading form data: {str(e)}")

    def create_booking(self, booking_data: Dict) -> Dict:
        """
        Create new booking

        Args:
            booking_data: Dict with booking fields

        Returns:
            Dict with success/error status
        """
        self.require_permission("user")

        try:
            with self.get_session() as session:
                # Generate confirmation code if not provided
                confirmation_code = booking_data.get("confirmation_code")
                if not confirmation_code:
                    confirmation_code = f"OFF-{uuid.uuid4().hex[:8].upper()}"

                # Calculate nights
                start_date = booking_data["start_date"]
                end_date = booking_data["end_date"]
                num_nights = (end_date - start_date).days

                # Get property details for listing name
                prop = session.get(Property, booking_data["property_id"])
                property_short = prop.property_short if prop else None
                airbnb_name = (
                    prop.airbnb_name.strip() if prop and prop.airbnb_name else ""
                )
                listing_name = (
                    airbnb_name
                    if airbnb_name and airbnb_name != property_short
                    else None
                )

                new_booking = Booking(
                    property_id=booking_data["property_id"],
                    channel_id=booking_data["channel_id"],
                    confirmation_code=confirmation_code,
                    start_date=start_date,
                    end_date=end_date,
                    num_nights=num_nights,
                    total_payout_vnd=booking_data["total_payout_vnd"],
                    guest_name=booking_data.get("guest_name"),
                    guest_contact=booking_data.get("guest_contact"),
                    status="xác nhận",
                    booking_date=date.today(),
                    salesperson_id=booking_data.get("salesperson_id"),
                    notes=booking_data.get("notes"),
                    listing_raw=listing_name,
                    # TODO: Add created_by when audit system ready
                    # created_by=self.user_id
                )

                session.add(new_booking)
                session.commit()
                session.refresh(new_booking)

                self.log_action(
                    "create",
                    "booking",
                    new_booking.id,
                    {
                        "property_id": new_booking.property_id,
                        "total_payout_vnd": new_booking.total_payout_vnd,
                    },
                )

                return self.format_success_response(
                    new_booking, "Booking created successfully"
                )

        except Exception as e:
            return self.format_error_response(f"Error creating booking: {str(e)}")

    def get_edit_booking_form_data(self, booking_id: int) -> Dict:
        """
        Get data for edit booking form

        Args:
            booking_id: ID of booking to edit

        Returns:
            Dict with booking and form data
        """
        self.require_permission("user")

        try:
            with self.get_session() as session:
                booking = session.get(Booking, booking_id)
                if not booking:
                    return self.format_error_response(
                        "Booking not found", {"booking_id": booking_id}
                    )

                # TODO: Check user access when audit system ready

                properties = session.exec(
                    select(Property).order_by(Property.property_name)
                ).all()
                channels = session.exec(
                    select(Channel).order_by(Channel.channel_name)
                ).all()
                salespeople = session.exec(
                    select(Salesperson).where(Salesperson.is_active)
                ).all()

                return self.format_success_response(
                    {
                        "booking": booking,
                        "properties": properties,
                        "channels": channels,
                        "salespeople": salespeople,
                    }
                )

        except Exception as e:
            return self.format_error_response(f"Error loading edit form: {str(e)}")

    def update_booking(self, booking_id: int, booking_data: Dict) -> Dict:
        """
        Update existing booking

        Args:
            booking_id: ID of booking to update
            booking_data: Dict with updated fields

        Returns:
            Dict with success/error status
        """
        self.require_permission("user")

        try:
            with self.get_session() as session:
                booking = session.get(Booking, booking_id)
                if not booking:
                    return self.format_error_response(
                        "Booking not found", {"booking_id": booking_id}
                    )

                # TODO: Check user access when audit system ready

                # Update fields
                booking.property_id = booking_data["property_id"]
                booking.channel_id = booking_data["channel_id"]
                booking.start_date = booking_data["start_date"]
                booking.end_date = booking_data["end_date"]
                booking.num_nights = (
                    booking_data["end_date"] - booking_data["start_date"]
                ).days
                booking.total_payout_vnd = booking_data["total_payout_vnd"]
                booking.guest_name = booking_data.get("guest_name")
                booking.guest_contact = booking_data.get("guest_contact")
                booking.salesperson_id = booking_data.get("salesperson_id")
                booking.notes = booking_data.get("notes")
                # TODO: Add updated_by when audit system ready

                session.add(booking)
                session.commit()

                self.log_action(
                    "update",
                    "booking",
                    booking_id,
                    {
                        "property_id": booking.property_id,
                        "total_payout_vnd": booking.total_payout_vnd,
                    },
                )

                return self.format_success_response(
                    booking, "Booking updated successfully"
                )

        except Exception as e:
            return self.format_error_response(f"Error updating booking: {str(e)}")

    def delete_booking(self, booking_id: int) -> Dict:
        """
        Delete booking

        Args:
            booking_id: ID of booking to delete

        Returns:
            Dict with success/error status
        """
        self.require_permission("manager")  # Only managers+ can delete

        try:
            with self.get_session() as session:
                booking = session.get(Booking, booking_id)
                if not booking:
                    return self.format_error_response(
                        "Booking not found", {"booking_id": booking_id}
                    )

                # TODO: Check user access when audit system ready

                session.delete(booking)
                session.commit()

                self.log_action("delete", "booking", booking_id)

                return self.format_success_response(
                    None, "Booking deleted successfully"
                )

        except Exception as e:
            return self.format_error_response(f"Error deleting booking: {str(e)}")

    # ============ ROOM ASSIGNMENT METHODS ============

    def get_booking_room_assignment(self, booking_id: int) -> Dict:
        """
        Get room assignment for a booking

        Args:
            booking_id: ID of booking

        Returns:
            Dict with room assignment data or None if no assignment
        """
        try:
            assignment = self.session.exec(
                select(RoomAssignment).where(RoomAssignment.booking_id == booking_id)
            ).first()

            return {"success": True, "data": assignment}

        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching room assignment: {str(e)}",
                "data": None,
            }

    def create_room_assignment(self, booking_id: int, assignment_data: Dict) -> Dict:
        """
        Create or update room assignment for a booking

        Args:
            booking_id: ID of booking
            assignment_data: Dict with assignment fields

        Returns:
            Dict with success/error status
        """
        try:
            # Check if booking exists
            booking = self.session.get(Booking, booking_id)
            if not booking:
                return {"success": False, "message": "Booking not found", "data": None}

            # Check if assignment already exists
            existing = self.session.exec(
                select(RoomAssignment).where(RoomAssignment.booking_id == booking_id)
            ).first()

            if existing:
                # Update existing assignment
                existing.booked_room = assignment_data.get("booked_room")
                existing.actual_room = assignment_data.get("actual_room")
                existing.revenue_attribution = assignment_data.get(
                    "revenue_attribution", "actual_room"
                )
                existing.change_reason = assignment_data.get("change_reason")
                existing.changed_date = assignment_data.get("changed_date")
                existing.changed_by = assignment_data.get("changed_by")
                existing.notes = assignment_data.get("notes")
                existing.updated_at = datetime.utcnow()

                self.session.add(existing)
                self.session.commit()

                return {
                    "success": True,
                    "data": existing,
                    "message": "Room assignment updated successfully",
                }
            else:
                # Create new assignment
                new_assignment = RoomAssignment(
                    booking_id=booking_id,
                    booked_room=assignment_data.get("booked_room"),
                    actual_room=assignment_data.get("actual_room"),
                    revenue_attribution=assignment_data.get(
                        "revenue_attribution", "actual_room"
                    ),
                    change_reason=assignment_data.get("change_reason"),
                    changed_date=assignment_data.get("changed_date"),
                    changed_by=assignment_data.get("changed_by"),
                    notes=assignment_data.get("notes"),
                )

                self.session.add(new_assignment)
                self.session.commit()
                self.session.refresh(new_assignment)

                return {
                    "success": True,
                    "data": new_assignment,
                    "message": "Room assignment created successfully",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating room assignment: {str(e)}",
                "data": None,
            }

    def get_room_assignment_history(self, booking_id: int) -> Dict:
        """
        Get history of room assignments for a booking

        Args:
            booking_id: ID of booking

        Returns:
            Dict with assignment history
        """
        try:
            with self.get_session() as session:
                assignments = session.exec(
                    select(RoomAssignment)
                    .where(RoomAssignment.booking_id == booking_id)
                    .order_by(RoomAssignment.created_at.desc())
                ).all()

                return self.format_success_response(
                    {
                        "booking_id": booking_id,
                        "assignments": assignments,
                        "has_room_changes": len(assignments) > 0
                        and any(
                            a.booked_room != a.actual_room
                            for a in assignments
                            if a.booked_room and a.actual_room
                        ),
                    }
                )

        except Exception as e:
            return self.format_error_response(
                f"Error fetching assignment history: {str(e)}"
            )

    def calculate_room_revenue_attribution(self, booking_id: int) -> Dict:
        """
        Calculate revenue attribution based on room assignment

        Args:
            booking_id: ID of booking

        Returns:
            Dict with revenue attribution details
        """
        try:
            booking = self.session.get(Booking, booking_id)
            if not booking:
                return {"success": False, "message": "Booking not found", "data": None}

            assignment = self.session.exec(
                select(RoomAssignment).where(RoomAssignment.booking_id == booking_id)
            ).first()

            total_revenue = booking.total_payout_vnd or 0

            if (
                not assignment
                or not assignment.actual_room
                or not assignment.booked_room
            ):
                # No room change, revenue goes to booked property
                return {
                    "success": True,
                    "data": {
                        "booking_id": booking_id,
                        "total_revenue": total_revenue,
                        "attribution_method": "no_change",
                        "booked_room_revenue": total_revenue,
                        "actual_room_revenue": 0,
                        "room_change": False,
                    },
                }

            # Room change detected
            room_change = assignment.booked_room != assignment.actual_room

            if not room_change:
                return {
                    "success": True,
                    "data": {
                        "booking_id": booking_id,
                        "total_revenue": total_revenue,
                        "attribution_method": "no_change",
                        "booked_room_revenue": total_revenue,
                        "actual_room_revenue": 0,
                        "room_change": False,
                    },
                }

            # Calculate attribution based on method
            attribution_method = assignment.revenue_attribution or "actual_room"

            if attribution_method == "booked_room":
                booked_revenue = total_revenue
                actual_revenue = 0
            elif attribution_method == "actual_room":
                booked_revenue = 0
                actual_revenue = total_revenue
            elif attribution_method == "split":
                booked_revenue = total_revenue // 2
                actual_revenue = total_revenue - booked_revenue
            else:
                # Default to actual room
                booked_revenue = 0
                actual_revenue = total_revenue

            return {
                "success": True,
                "data": {
                    "booking_id": booking_id,
                    "total_revenue": total_revenue,
                    "attribution_method": attribution_method,
                    "booked_room": assignment.booked_room,
                    "actual_room": assignment.actual_room,
                    "booked_room_revenue": booked_revenue,
                    "actual_room_revenue": actual_revenue,
                    "room_change": True,
                    "change_reason": assignment.change_reason,
                    "changed_date": assignment.changed_date,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error calculating revenue attribution: {str(e)}",
                "data": None,
            }

    # ============ /ROOM ASSIGNMENT METHODS ============
