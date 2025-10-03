"""
Revenue Service - Monthly Reports and Analytics
=============================================

Handles:
- Monthly revenue reports with complex aggregations
- Building/Property/Channel/Salesperson grouping
- KPI calculations (occupancy, ADR, RevPAR)
- Chart data generation (trends + pie charts)  
- Extra charges and expense integration
"""

import calendar
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

import pandas as pd
from sqlalchemy import not_, or_
from sqlmodel import func, select

from models import (Booking, Channel, ExpenseCategory, ExtraCharge, Property,
                    Salesperson)

from .base import BaseService


class RevenueService(BaseService):
    """Revenue reporting and analytics with user context support"""
    
    def compute_monthly_report(self, start_date: date, end_date: date, group_by: str) -> Tuple[List[Dict], Dict, Dict]:
        """
        Main monthly report computation with comprehensive analytics
        
        Returns:
            Tuple of (rows_data, totals_kpis, chart_data)
        """
        try:
            # Load base data
            bookings = self._load_bookings()
            props = {p.id: p for p in self.session.exec(select(Property)).all()}
            chans = {c.id: c for c in self.session.exec(select(Channel)).all()}
            sales_map = {s.id: s for s in self.session.exec(select(Salesperson)).all()}
            
            # Load extra charges
            extra_charges_map = self._load_extra_charges(start_date, end_date)
            
            # Load expense categories  
            categories = self.session.exec(select(ExpenseCategory)).all()
            {cat.id: cat.name for cat in categories}
            
            # Process bookings into aggregated results
            results, monthly_channel_data = self._process_bookings(
                bookings, props, chans, sales_map, 
                start_date, end_date, group_by
            )
            
            # Integrate extra charges into results
            self._integrate_extra_charges(results, extra_charges_map)
            
            # Ensure all groups/months represented (even if no data)
            self._ensure_complete_dataset(results, props, chans, sales_map, start_date, end_date, group_by)
            
            # Generate final report rows
            rows = self._generate_report_rows(results, props, bookings, chans, sales_map, group_by)
            
            # Calculate totals/KPIs
            totals = self._calculate_totals(rows)
            
            # Generate chart data
            charts = self._generate_chart_data(results, self._calculate_channel_totals(bookings, chans), monthly_channel_data)
            
            self.log_activity("compute_monthly_report", {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(), 
                "group_by": group_by,
                "total_rows": len(rows),
                "total_revenue": totals.get("total_revenue", 0)
            })
            
            return rows, totals, charts
            
        except Exception as e:
            error_msg = f"Failed to compute monthly report: {str(e)}"
            self.log_activity("compute_monthly_report_error", {"error": error_msg})
            raise Exception(error_msg)
    
    # ==================
    # PRIVATE HELPERS
    # ==================
    
    def _load_bookings(self) -> List[Booking]:
        """Load all non-cancelled bookings"""
        return self.session.exec(
            select(Booking).where(
                or_(
                    Booking.status.is_(None),
                    not_(Booking.status.ilike("%hủy%"))
                )
            )
        ).all()
    
    def _load_extra_charges(self, start_date: date, end_date: date) -> Dict:
        """Load extra charges for date range"""
        extra_charges = self.session.exec(
            select(ExtraCharge.charge_month, ExtraCharge.charge_name, func.sum(ExtraCharge.charge_amount))
            .where(ExtraCharge.charge_month >= start_date.strftime("%Y-%m"))
            .where(ExtraCharge.charge_month <= end_date.strftime("%Y-%m"))
            .group_by(ExtraCharge.charge_month, ExtraCharge.charge_name)
        ).all()
        
        extra_charges_map = defaultdict(lambda: defaultdict(float))
        for ec in extra_charges:
            charge_month = date(int(ec[0][:4]), int(ec[0][5:]), 1)  # "YYYY-MM" → date
            extra_charges_map[charge_month][ec[1]] += ec[2]
            
        return extra_charges_map
    
    def _process_bookings(self, bookings: List[Booking], props: Dict, chans: Dict, 
                         sales_map: Dict, start_date: date, end_date: date, group_by: str) -> Dict:
        """Process all bookings into aggregated results by month/group"""
        results = defaultdict(lambda: {
            "sold_nights": 0, "revenue": 0.0, "commission": 0.0, 
            "prop_ids": set(), "expenses": defaultdict(float)
        })
        
        # Track monthly channel data for charts
        monthly_channel_data = defaultdict(lambda: defaultdict(float))
        
        for b in bookings:
            if not self._is_valid_booking(b):
                continue
            
            # Calculate booking overlap with date range
            cur = max(b.start_date, start_date)
            last = min(b.end_date, end_date + timedelta(days=1))
            if cur >= last:
                continue
            
            # Determine grouping value
            group_val = self._get_group_value(b, props, chans, sales_map, group_by)
            
            # Calculate nightly metrics
            nightly_revenue = (b.total_payout_vnd or 0) / max(b.num_nights, 1)
            sale = sales_map.get(b.salesperson_id)
            nightly_commission = nightly_revenue * (sale.commission_rate if sale else 0)
            
            # Get channel name for tracking
            chan_name = chans.get(b.channel_id).channel_name if b.channel_id in chans else "N/A"
            
            # Process each night in the booking
            d = cur
            while d < last:
                mk = date(d.year, d.month, 1)  # Month key
                key = (mk, group_val)
                
                results[key]["sold_nights"] += 1
                results[key]["revenue"] += nightly_revenue  
                results[key]["commission"] += nightly_commission
                
                # Track monthly channel revenue for charts
                monthly_channel_data[mk][chan_name] += nightly_revenue
                
                if b.property_id:
                    results[key]["prop_ids"].add(b.property_id)
                
                d += timedelta(days=1)
        
        return results, monthly_channel_data
    
    def _is_valid_booking(self, booking: Booking) -> bool:
        """Check if booking has required data for processing"""
        return bool(
            booking.start_date and booking.end_date and 
            booking.num_nights and booking.total_payout_vnd is not None
        )
    
    def _get_group_value(self, booking: Booking, props: Dict, chans: Dict, sales_map: Dict, group_by: str) -> str:
        """Get the grouping value for a booking based on group_by parameter"""
        if group_by == "building":
            p = props.get(booking.property_id)
            return p.building_name if p else "N/A"
        elif group_by == "channel":
            return chans.get(booking.channel_id).channel_name if booking.channel_id in chans else "N/A"
        elif group_by == "salesperson":
            sale = sales_map.get(booking.salesperson_id)
            return sale.name if sale else "Không có"
        else:  # property
            p = props.get(booking.property_id)
            return (p.property_short or p.property_name) if p else "N/A"
    
    def _integrate_extra_charges(self, results: Dict, extra_charges_map: Dict):
        """Integrate extra charges into monthly results"""
        for mk, charges in extra_charges_map.items():
            for cat_id, amount in charges.items():
                for key in results.keys():
                    if key[0] == mk:  # Same month
                        results[key]["expenses"][cat_id] += amount
    
    def _ensure_complete_dataset(self, results: Dict, props: Dict, chans: Dict, sales_map: Dict, 
                                start_date: date, end_date: date, group_by: str):
        """Ensure all groups/months are represented even if no bookings"""
        # Get all possible groups
        if group_by == "building":
            all_groups = {p.building_name or "N/A" for p in props.values()}
        elif group_by == "channel":
            all_groups = {c.channel_name for c in chans.values()}
        elif group_by == "salesperson":
            all_groups = {s.name for s in sales_map.values()}
        else:
            all_groups = {(p.property_short or p.property_name or "N/A") for p in props.values()}
        
        # Get all months in range
        months_in_range = set(date(d.year, d.month, 1) for d in pd.date_range(start_date, end_date))
        
        # Ensure all combinations exist
        for mk in months_in_range:
            for g in all_groups:
                key = (mk, g)
                if key not in results:
                    results[key] = {
                        "sold_nights": 0, "revenue": 0.0, "commission": 0.0, 
                        "prop_ids": set(), "expenses": defaultdict(float)
                    }
    
    def _generate_report_rows(self, results: Dict, props: Dict, bookings: List, chans: Dict, sales_map: Dict, group_by: str) -> List[Dict]:
        """Generate final report rows with calculated metrics"""
        rows = []
        
        for (mk, group_val), agg in sorted(results.items()):
            sold = agg["sold_nights"] 
            rev = int(round(agg["revenue"]))
            comm = int(round(agg["commission"]))
            adr = int(round(rev / sold)) if sold else 0
            
            # Calculate available nights based on group type
            active_props = self._get_active_properties_count(group_val, props, bookings, chans, sales_map, group_by)
            avail = active_props * calendar.monthrange(mk.year, mk.month)[1]  # days in month
            
            vacant = avail - sold
            occ = round((sold / avail) * 100, 1) if avail else 0.0
            revpar = int(round(rev / avail)) if avail else 0
            
            rows.append({
                "month": mk, "group": group_val, "sold_nights": sold,
                "vacant_nights": vacant, "revenue_vnd": rev, "adr_vnd": adr,
                "available_nights": avail, "occupancy_pct": occ,
                "revpar_vnd": revpar, "commission_vnd": comm
            })
        
        return rows
    
    def _get_active_properties_count(self, group_val: str, props: Dict, bookings: List, chans: Dict, sales_map: Dict, group_by: str) -> int:
        """Get count of active properties for a specific group"""
        if group_by == "building":
            return len([p for p in props.values() if p.building_name == group_val])
        elif group_by == "channel":
            return len([b for b in bookings if chans.get(b.channel_id) and chans[b.channel_id].channel_name == group_val])
        elif group_by == "salesperson":
            return len([b for b in bookings if sales_map.get(b.salesperson_id) and sales_map[b.salesperson_id].name == group_val])
        else:  # property
            return 1
    
    def _calculate_totals(self, rows: List[Dict]) -> Dict[str, Any]:
        """Calculate total KPIs from report rows"""
        total_revenue = int(round(sum(r["revenue_vnd"] for r in rows)))
        total_commission = int(round(sum(r["commission_vnd"] for r in rows)))
        total_sold_nights = sum(r["sold_nights"] for r in rows)
        total_vacant_nights = sum(r["vacant_nights"] for r in rows)
        total_available_nights = sum(r["available_nights"] for r in rows)
        
        total_occupancy_pct = round((total_sold_nights / total_available_nights) * 100, 1) if total_available_nights else 0.0
        total_revpar_vnd = int(round(total_revenue / total_available_nights)) if total_available_nights else 0
        
        return {
            "total_rows": len(rows),
            "total_revenue": total_revenue,
            "total_commission": total_commission, 
            "total_sold_nights": total_sold_nights,
            "total_vacant_nights": total_vacant_nights,
            "total_available_nights": total_available_nights,
            "total_occupancy_pct": total_occupancy_pct,
            "total_revpar_vnd": total_revpar_vnd
        }
    
    def _calculate_channel_totals(self, bookings: List[Booking], chans: Dict) -> Dict[str, float]:
        """Calculate revenue totals by channel for pie chart"""
        channel_totals = defaultdict(float)
        
        for b in bookings:
            if not self._is_valid_booking(b):
                continue
            
            chan_name = chans.get(b.channel_id).channel_name if b.channel_id in chans else "N/A"
            nightly_revenue = (b.total_payout_vnd or 0) / max(b.num_nights, 1)
            total_revenue = nightly_revenue * b.num_nights
            
            channel_totals[chan_name] += total_revenue
        
        return dict(channel_totals)
    
    def _generate_chart_data(self, results: Dict, channel_totals: Dict, monthly_channel_data: Dict) -> Dict[str, Any]:
        """Generate chart data for trends and channel breakdown"""
        # Monthly trend aggregation
        monthly_trend = defaultdict(lambda: {"sold_nights": 0, "revenue": 0.0, "commission": 0.0})
        for (mk, group_val), agg in results.items():
            monthly_trend[mk]["sold_nights"] += agg["sold_nights"]
            monthly_trend[mk]["revenue"] += agg["revenue"] 
            monthly_trend[mk]["commission"] += agg["commission"]
        
        # Sort and format trend data
        sorted_trend = sorted(monthly_trend.items())
        trend_months = [m[0].strftime("%Y-%m") for m in sorted_trend]
        trend_data = [m[1] for m in sorted_trend]
        
        # Generate channel-specific monthly data for line chart
        airbnb_monthly = []
        offline_monthly = []
        
        for mk, _ in sorted_trend:
            month_channels = monthly_channel_data.get(mk, {})
            airbnb_rev = sum(rev for chan, rev in month_channels.items() if "airbnb" in chan.lower())
            offline_rev = sum(rev for chan, rev in month_channels.items() if chan.lower() == "offline")
            
            airbnb_monthly.append(int(airbnb_rev))
            offline_monthly.append(int(offline_rev))
        
        # Channel revenue pie chart
        sorted_channels = sorted(channel_totals.items(), key=lambda x: x[1], reverse=True)
        total_channel_revenue = sum(channel_totals.values())
        
        channel_pie_data = [
            {
                "channel": chan, 
                "revenue": int(round(rev)),
                "percentage": round((rev / total_channel_revenue) * 100, 2) if total_channel_revenue > 0 else 0
            }
            for chan, rev in sorted_channels
        ]
        
        return {
            "trend_months": trend_months,
            "trend_data": trend_data,
            "channel_pie": channel_pie_data,
            "airbnb_monthly": airbnb_monthly,
            "offline_monthly": offline_monthly
        }
    
    # ==================
    # PUBLIC UTILITIES  
    # ==================
    
    def get_monthly_summary(self, month: date) -> Dict[str, Any]:
        """Get summary statistics for a specific month"""
        start_date = month.replace(day=1)
        end_date = (start_date.replace(month=start_date.month % 12 + 1) - timedelta(days=1))
        
        rows, totals, _ = self.compute_monthly_report(start_date, end_date, "property")
        
        return {
            "month": month.strftime("%Y-%m"),
            "total_revenue": totals["total_revenue"],
            "total_bookings": totals["total_sold_nights"],
            "occupancy_rate": totals["total_occupancy_pct"],
            "average_adr": totals["total_revenue"] // max(totals["total_sold_nights"], 1)
        }