"""
Salesperson Service - Sales Team and Commission Management
========================================================

Handles:
- Salesperson CRUD operations
- Commission calculations and tracking
- Active/inactive status management
- Sales performance analytics
- Integration with booking assignments
"""

from sqlmodel import select, func
from typing import List, Dict, Any, Optional
from decimal import Decimal

from models import Salesperson, Booking
from .base import BaseService


class SalespersonService(BaseService):
    """Salesperson and commission management service with user context support"""
    
    # ==================
    # CRUD OPERATIONS
    # ==================
    
    def get_all_salespeople(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get all salespeople with optional active filter"""
        query = select(Salesperson)
        
        if active_only:
            query = query.where(Salesperson.is_active == True)
            
        query = query.order_by(Salesperson.name)
        salespeople = self.session.exec(query).all()
        
        # Add booking counts and commission totals
        result = []
        for sp in salespeople:
            booking_count = self._get_booking_count(sp.id)
            total_commission = self._calculate_total_commission(sp.id)
            
            result.append({
                "id": sp.id,
                "name": sp.name,
                "email": sp.email,
                "phone": sp.phone,
                "commission_rate": sp.commission_rate,
                "commission_rate_pct": round(sp.commission_rate * 100, 2),
                "is_active": sp.is_active,
                "booking_count": booking_count,
                "total_commission_vnd": int(total_commission) if total_commission else 0
            })
        
        self.log_activity("get_all_salespeople", {
            "total_count": len(result),
            "active_only": active_only
        })
        
        return result
    
    def get_active_salespeople(self) -> List[Salesperson]:
        """Get only active salespeople for dropdowns/forms"""
        return self.session.exec(
            select(Salesperson).where(Salesperson.is_active == True)
            .order_by(Salesperson.name)
        ).all()
    
    def get_salesperson_by_id(self, salesperson_id: int) -> Optional[Dict[str, Any]]:
        """Get single salesperson with detailed info"""
        salesperson = self.session.get(Salesperson, salesperson_id)
        if not salesperson:
            return None
        
        booking_count = self._get_booking_count(salesperson_id)
        total_commission = self._calculate_total_commission(salesperson_id)
        
        return {
            "id": salesperson.id,
            "name": salesperson.name,
            "email": salesperson.email,
            "phone": salesperson.phone,
            "commission_rate": salesperson.commission_rate,
            "commission_rate_pct": round(salesperson.commission_rate * 100, 2),
            "is_active": salesperson.is_active,
            "booking_count": booking_count,
            "total_commission_vnd": int(total_commission) if total_commission else 0
        }
    
    def create_salesperson(self, name: str, commission_rate_pct: float, 
                          email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        """Create new salesperson with validation"""
        try:
            # Check permissions if user context available
            if self.current_user:
                if not self.check_permission("salesperson_create"):
                    return self.error_response("Insufficient permissions to create salesperson", 403)
            
            # Validate inputs
            if not name or not name.strip():
                return self.error_response("Salesperson name is required", 400)
            
            if commission_rate_pct < 0 or commission_rate_pct > 100:
                return self.error_response("Commission rate must be between 0 and 100 percent", 400)
            
            # Check for duplicate names
            existing = self.session.exec(
                select(Salesperson).where(Salesperson.name == name.strip())
            ).first()
            if existing:
                return self.error_response("A salesperson with this name already exists", 409)
            
            # Convert percentage to decimal
            commission_rate = commission_rate_pct / 100.0
            
            # Create new salesperson
            new_salesperson = Salesperson(
                name=name.strip(),
                email=email.strip() if email else None,
                phone=phone.strip() if phone else None,
                commission_rate=commission_rate,
                is_active=True
            )
            
            self.session.add(new_salesperson)
            self.session.commit()
            self.session.refresh(new_salesperson)
            
            self.log_activity("create_salesperson", {
                "salesperson_id": new_salesperson.id,
                "name": name,
                "commission_rate_pct": commission_rate_pct
            })
            
            return self.success_response("Salesperson created successfully", {
                "salesperson_id": new_salesperson.id,
                "name": new_salesperson.name
            })
            
        except Exception as e:
            self.session.rollback()
            return self.error_response(f"Failed to create salesperson: {str(e)}", 500)
    
    def update_salesperson(self, salesperson_id: int, name: Optional[str] = None,
                          email: Optional[str] = None, phone: Optional[str] = None,
                          commission_rate_pct: Optional[float] = None,
                          is_active: Optional[bool] = None) -> Dict[str, Any]:
        """Update salesperson information"""
        try:
            # Check permissions if user context available
            if self.current_user:
                if not self.check_permission("salesperson_update"):
                    return self.error_response("Insufficient permissions to update salesperson", 403)
            
            salesperson = self.session.get(Salesperson, salesperson_id)
            if not salesperson:
                return self.error_response("Salesperson not found", 404)
            
            # Update fields if provided
            if name is not None:
                if not name.strip():
                    return self.error_response("Salesperson name cannot be empty", 400)
                salesperson.name = name.strip()
            
            if email is not None:
                salesperson.email = email.strip() if email else None
            
            if phone is not None:
                salesperson.phone = phone.strip() if phone else None
            
            if commission_rate_pct is not None:
                if commission_rate_pct < 0 or commission_rate_pct > 100:
                    return self.error_response("Commission rate must be between 0 and 100 percent", 400)
                salesperson.commission_rate = commission_rate_pct / 100.0
            
            if is_active is not None:
                salesperson.is_active = is_active
            
            self.session.add(salesperson)
            self.session.commit()
            
            self.log_activity("update_salesperson", {
                "salesperson_id": salesperson_id,
                "updated_fields": {k: v for k, v in {
                    "name": name, "email": email, "phone": phone,
                    "commission_rate_pct": commission_rate_pct, "is_active": is_active
                }.items() if v is not None}
            })
            
            return self.success_response("Salesperson updated successfully", {
                "salesperson_id": salesperson_id
            })
            
        except Exception as e:
            self.session.rollback()
            return self.error_response(f"Failed to update salesperson: {str(e)}", 500)
    
    def deactivate_salesperson(self, salesperson_id: int) -> Dict[str, Any]:
        """Deactivate salesperson (soft delete)"""
        return self.update_salesperson(salesperson_id, is_active=False)
    
    def activate_salesperson(self, salesperson_id: int) -> Dict[str, Any]:
        """Activate salesperson"""
        return self.update_salesperson(salesperson_id, is_active=True)
    
    # ============================
    # COMMISSION CALCULATIONS
    # ============================
    
    def calculate_commission_for_booking(self, booking_id: int) -> Dict[str, Any]:
        """Calculate commission for a specific booking"""
        try:
            booking = self.session.get(Booking, booking_id)
            if not booking:
                return self.error_response("Booking not found", 404)
            
            if not booking.salesperson_id:
                return self.success_response("No salesperson assigned", {
                    "commission_vnd": 0,
                    "commission_rate": 0
                })
            
            salesperson = self.session.get(Salesperson, booking.salesperson_id)
            if not salesperson:
                return self.error_response("Salesperson not found", 404)
            
            # Calculate commission
            total_payout = booking.total_payout_vnd or 0
            commission_amount = total_payout * salesperson.commission_rate
            
            return self.success_response("Commission calculated", {
                "booking_id": booking_id,
                "salesperson_name": salesperson.name,
                "total_payout_vnd": int(total_payout),
                "commission_rate": salesperson.commission_rate,
                "commission_rate_pct": round(salesperson.commission_rate * 100, 2),
                "commission_vnd": int(commission_amount)
            })
            
        except Exception as e:
            return self.error_response(f"Failed to calculate commission: {str(e)}", 500)
    
    def get_salesperson_performance(self, salesperson_id: int, 
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed performance metrics for a salesperson"""
        try:
            salesperson = self.session.get(Salesperson, salesperson_id)
            if not salesperson:
                return self.error_response("Salesperson not found", 404)
            
            # Build query for bookings
            query = select(Booking).where(Booking.salesperson_id == salesperson_id)
            
            if start_date:
                query = query.where(Booking.start_date >= start_date)
            if end_date:
                query = query.where(Booking.end_date <= end_date)
            
            bookings = self.session.exec(query).all()
            
            # Calculate metrics
            total_bookings = len(bookings)
            total_nights = sum(b.num_nights or 0 for b in bookings)
            total_revenue = sum(b.total_payout_vnd or 0 for b in bookings)
            total_commission = total_revenue * salesperson.commission_rate
            
            # Average metrics
            avg_booking_value = int(total_revenue / total_bookings) if total_bookings > 0 else 0
            avg_nights_per_booking = round(total_nights / total_bookings, 1) if total_bookings > 0 else 0
            
            return self.success_response("Performance data retrieved", {
                "salesperson": {
                    "id": salesperson.id,
                    "name": salesperson.name,
                    "commission_rate_pct": round(salesperson.commission_rate * 100, 2)
                },
                "metrics": {
                    "total_bookings": total_bookings,
                    "total_nights": total_nights,
                    "total_revenue_vnd": int(total_revenue),
                    "total_commission_vnd": int(total_commission),
                    "avg_booking_value_vnd": avg_booking_value,
                    "avg_nights_per_booking": avg_nights_per_booking
                },
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            })
            
        except Exception as e:
            return self.error_response(f"Failed to get performance data: {str(e)}", 500)
    
    # ==================
    # HELPER METHODS
    # ==================
    
    def _get_booking_count(self, salesperson_id: int) -> int:
        """Get total booking count for salesperson"""
        return self.session.exec(
            select(func.count()).where(Booking.salesperson_id == salesperson_id)
        ).one()
    
    def _calculate_total_commission(self, salesperson_id: int) -> float:
        """Calculate total commission earned by salesperson"""
        salesperson = self.session.get(Salesperson, salesperson_id)
        if not salesperson:
            return 0.0
        
        # Get all bookings for this salesperson
        total_payout = self.session.exec(
            select(func.sum(Booking.total_payout_vnd)).where(
                Booking.salesperson_id == salesperson_id
            )
        ).one() or 0
        
        return float(total_payout) * salesperson.commission_rate
    
    # ==================
    # BUSINESS QUERIES
    # ==================
    
    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing salespeople by commission"""
        all_salespeople = self.get_all_salespeople(active_only=True)
        
        # Sort by total commission descending
        sorted_salespeople = sorted(
            all_salespeople, 
            key=lambda x: x["total_commission_vnd"], 
            reverse=True
        )
        
        return sorted_salespeople[:limit]
    
    def assign_booking_to_salesperson(self, booking_id: int, salesperson_id: Optional[int]) -> Dict[str, Any]:
        """Assign or unassign a booking to/from a salesperson"""
        try:
            # Check permissions if user context available
            if self.current_user:
                if not self.check_permission("booking_assign"):
                    return self.error_response("Insufficient permissions to assign bookings", 403)
            
            booking = self.session.get(Booking, booking_id)
            if not booking:
                return self.error_response("Booking not found", 404)
            
            # Validate salesperson exists if provided
            if salesperson_id is not None:
                salesperson = self.session.get(Salesperson, salesperson_id)
                if not salesperson:
                    return self.error_response("Salesperson not found", 404)
                if not salesperson.is_active:
                    return self.error_response("Cannot assign to inactive salesperson", 400)
            
            # Update assignment
            old_salesperson_id = booking.salesperson_id
            booking.salesperson_id = salesperson_id
            
            self.session.add(booking)
            self.session.commit()
            
            self.log_activity("assign_booking_to_salesperson", {
                "booking_id": booking_id,
                "old_salesperson_id": old_salesperson_id,
                "new_salesperson_id": salesperson_id
            })
            
            action = "assigned" if salesperson_id else "unassigned"
            return self.success_response(f"Booking {action} successfully", {
                "booking_id": booking_id,
                "salesperson_id": salesperson_id
            })
            
        except Exception as e:
            self.session.rollback()
            return self.error_response(f"Failed to assign booking: {str(e)}", 500)