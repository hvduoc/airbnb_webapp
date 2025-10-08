"""
AnalyticsService - Business Intelligence Dashboard Data
======================================================

Service này aggregate data từ multiple sources để tạo dashboard KPIs:
- Revenue vs Expense analysis by property
- Occupancy rates và utilization metrics
- ARPU (Average Revenue Per User/Booking)
- Top properties by profit margin
- Monthly trends và forecasting

Uses existing RevenueService và ExpenseService để avoid duplication.

Author: AI Assistant
Date: 2025-10-03
"""

from datetime import date, timedelta
from typing import Dict, Optional, Any
from sqlmodel import select, func, and_

from .base_service import BaseService
from .revenue_service import RevenueService
from .expense_service import ExpenseService
from models import Booking, Property, Expense


class AnalyticsService(BaseService):
    """
    AnalyticsService - Dashboard KPIs và business intelligence

    Features:
    - Revenue vs Expense comparisons
    - Occupancy và utilization rates
    - ARPU calculations
    - Property performance rankings
    - Monthly trends analysis
    - Permission enforcement: analytics.read
    """

    def get_revenue_vs_expense_dashboard(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Revenue vs Expense analysis by property cho dashboard

        Returns:
            {
                "summary": {
                    "total_revenue": int,
                    "total_expenses": int,
                    "net_profit": int,
                    "profit_margin": float,
                    "top_property_margin": float
                },
                "properties": [
                    {
                        "property_id": int,
                        "property_name": str,
                        "revenue": int,
                        "expenses": int,
                        "profit": int,
                        "margin": float,
                        "rank": int
                    }
                ],
                "charts": {
                    "revenue_chart": [...],
                    "expense_chart": [...],
                    "margin_chart": [...]
                }
            }
        """
        # Check permission
        self.require_permission("analytics", "read")

        # Get revenue data
        revenue_service = RevenueService(self.db, self.user)
        revenue_data = revenue_service.revenue_by_property(
            start_date, end_date, include_cancelled=False
        )

        # Get expense data
        expense_service = ExpenseService(self.db, self.user)
        expense_data = expense_service.summary_by_property(start_date, end_date)

        # Create property lookup maps
        revenue_map = {p["property_id"]: p for p in revenue_data["properties"]}
        expense_map = {p["property_id"]: p for p in expense_data["properties"]}

        # Combine data và calculate metrics
        combined_properties = []
        all_property_ids = set(revenue_map.keys()) | set(expense_map.keys())

        for property_id in all_property_ids:
            revenue_info = revenue_map.get(property_id, {})
            expense_info = expense_map.get(property_id, {})

            revenue = revenue_info.get("total_revenue", 0)
            expenses = expense_info.get("total_amount", 0)
            profit = revenue - expenses
            margin = (profit / revenue * 100) if revenue > 0 else 0

            combined_properties.append(
                {
                    "property_id": property_id,
                    "property_name": revenue_info.get("property_name")
                    or expense_info.get("property_name", f"Property {property_id}"),
                    "revenue": revenue,
                    "expenses": expenses,
                    "profit": profit,
                    "margin": round(margin, 2),
                    "revenue_formatted": f"{revenue:,} VNĐ",
                    "expenses_formatted": f"{expenses:,} VNĐ",
                    "profit_formatted": f"{profit:,} VNĐ",
                }
            )

        # Sort by profit margin (descending)
        combined_properties.sort(key=lambda x: x["margin"], reverse=True)

        # Add ranking
        for i, prop in enumerate(combined_properties):
            prop["rank"] = i + 1

        # Calculate summary metrics
        total_revenue = sum(p["revenue"] for p in combined_properties)
        total_expenses = sum(p["expenses"] for p in combined_properties)
        net_profit = total_revenue - total_expenses
        overall_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        top_property_margin = (
            combined_properties[0]["margin"] if combined_properties else 0
        )

        # Prepare chart data
        property_names = [
            p["property_name"][:15] + "..."
            if len(p["property_name"]) > 15
            else p["property_name"]
            for p in combined_properties[:10]
        ]
        revenue_chart = [p["revenue"] for p in combined_properties[:10]]
        expense_chart = [p["expenses"] for p in combined_properties[:10]]
        margin_chart = [p["margin"] for p in combined_properties[:10]]

        return {
            "summary": {
                "total_revenue": total_revenue,
                "total_expenses": total_expenses,
                "net_profit": net_profit,
                "profit_margin": round(overall_margin, 2),
                "top_property_margin": top_property_margin,
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d")
                    if start_date
                    else None,
                    "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
                },
                "formatted": {
                    "total_revenue": f"{total_revenue:,} VNĐ",
                    "total_expenses": f"{total_expenses:,} VNĐ",
                    "net_profit": f"{net_profit:,} VNĐ",
                },
            },
            "properties": combined_properties,
            "charts": {
                "property_names": property_names,
                "revenue_chart": revenue_chart,
                "expense_chart": expense_chart,
                "margin_chart": margin_chart,
            },
        }

    def get_occupancy_metrics(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate occupancy rates và utilization metrics

        Returns:
            {
                "summary": {
                    "overall_occupancy": float,
                    "total_nights_booked": int,
                    "total_nights_available": int,
                    "average_length_of_stay": float
                },
                "properties": [
                    {
                        "property_id": int,
                        "property_name": str,
                        "occupancy_rate": float,
                        "nights_booked": int,
                        "total_bookings": int,
                        "avg_stay_length": float
                    }
                ]
            }
        """
        # Check permission
        self.require_permission("analytics", "read")

        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Calculate date range
        date_range = (end_date - start_date).days + 1

        # Build occupancy query
        query = (
            select(
                Booking.property_id,
                Property.property_name,
                func.count(Booking.id).label("total_bookings"),
                func.sum(Booking.num_nights).label("nights_booked"),
                func.avg(Booking.num_nights).label("avg_stay_length"),
            )
            .select_from(
                Booking.__table__.join(
                    Property.__table__, Booking.property_id == Property.id
                )
            )
            .where(
                and_(
                    Booking.start_date >= start_date.strftime("%Y-%m-%d"),
                    Booking.end_date <= end_date.strftime("%Y-%m-%d"),
                    Booking.status.in_(
                        ["confirmed", "checked_in", "checked_out"]
                    ),  # Exclude cancelled
                )
            )
            .group_by(Booking.property_id, Property.property_name)
        )

        # Apply property filtering
        query = self.apply_property_filter(query, "property_id")

        # Execute query
        results = self.db.exec(query).all()

        # Calculate metrics
        properties = []
        total_nights_booked = 0
        total_bookings = 0

        for row in results:
            nights_booked = row.nights_booked or 0
            nights_available = date_range  # Simplified: assumes 1 property = 1 room
            occupancy_rate = (
                (nights_booked / nights_available * 100) if nights_available > 0 else 0
            )

            properties.append(
                {
                    "property_id": row.property_id,
                    "property_name": row.property_name,
                    "occupancy_rate": round(occupancy_rate, 2),
                    "nights_booked": nights_booked,
                    "nights_available": nights_available,
                    "total_bookings": row.total_bookings,
                    "avg_stay_length": round(float(row.avg_stay_length), 2)
                    if row.avg_stay_length
                    else 0,
                }
            )

            total_nights_booked += nights_booked
            total_bookings += row.total_bookings

        # Calculate overall metrics
        total_properties = len(properties)
        total_nights_available = total_properties * date_range
        overall_occupancy = (
            (total_nights_booked / total_nights_available * 100)
            if total_nights_available > 0
            else 0
        )
        avg_length_of_stay = (
            (total_nights_booked / total_bookings) if total_bookings > 0 else 0
        )

        # Sort by occupancy rate
        properties.sort(key=lambda x: x["occupancy_rate"], reverse=True)

        return {
            "summary": {
                "overall_occupancy": round(overall_occupancy, 2),
                "total_nights_booked": total_nights_booked,
                "total_nights_available": total_nights_available,
                "average_length_of_stay": round(avg_length_of_stay, 2),
                "total_properties": total_properties,
                "date_range_days": date_range,
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            },
            "properties": properties,
        }

    def get_arpu_metrics(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate ARPU (Average Revenue Per User/Booking)

        Returns:
            {
                "summary": {
                    "overall_arpu": float,
                    "total_revenue": int,
                    "total_bookings": int,
                    "arpu_trend": str
                },
                "properties": [
                    {
                        "property_id": int,
                        "property_name": str,
                        "arpu": float,
                        "revenue": int,
                        "bookings": int,
                        "rank": int
                    }
                ]
            }
        """
        # Check permission
        self.require_permission("analytics", "read")

        # Get revenue data với booking counts
        revenue_service = RevenueService(self.db, self.user)
        revenue_data = revenue_service.revenue_by_property(
            start_date, end_date, include_cancelled=False
        )

        # Calculate ARPU for each property
        properties = []
        for prop in revenue_data["properties"]:
            revenue = prop["total_revenue"]
            bookings = prop["total_bookings"]
            arpu = (revenue / bookings) if bookings > 0 else 0

            properties.append(
                {
                    "property_id": prop["property_id"],
                    "property_name": prop["property_name"],
                    "arpu": round(arpu, 0),
                    "arpu_formatted": f"{arpu:,.0f} VNĐ",
                    "revenue": revenue,
                    "revenue_formatted": f"{revenue:,} VNĐ",
                    "bookings": bookings,
                }
            )

        # Sort by ARPU (descending)
        properties.sort(key=lambda x: x["arpu"], reverse=True)

        # Add ranking
        for i, prop in enumerate(properties):
            prop["rank"] = i + 1

        # Calculate overall ARPU
        total_revenue = revenue_data["summary"]["total_revenue"]
        total_bookings = revenue_data["summary"]["total_bookings"]
        overall_arpu = (total_revenue / total_bookings) if total_bookings > 0 else 0

        return {
            "summary": {
                "overall_arpu": round(overall_arpu, 0),
                "overall_arpu_formatted": f"{overall_arpu:,.0f} VNĐ",
                "total_revenue": total_revenue,
                "total_revenue_formatted": f"{total_revenue:,} VNĐ",
                "total_bookings": total_bookings,
                "period": revenue_data["summary"]["period"],
            },
            "properties": properties,
        }

    def get_monthly_trends(self, months_back: int = 12) -> Dict[str, Any]:
        """
        Generate monthly trends cho revenue, expenses, bookings

        Returns:
            {
                "months": ["2024-11", "2024-12", "2025-01", ...],
                "revenue_trend": [1000000, 1200000, 1500000, ...],
                "expense_trend": [500000, 600000, 700000, ...],
                "booking_trend": [10, 12, 15, ...],
                "profit_trend": [500000, 600000, 800000, ...],
                "summary": {
                    "revenue_growth": float,
                    "expense_growth": float,
                    "booking_growth": float
                }
            }
        """
        # Check permission
        self.require_permission("analytics", "read")

        # Generate month list
        end_date = date.today()
        months = []
        for i in range(months_back):
            month_date = end_date.replace(day=1) - timedelta(days=i * 30)
            months.append(month_date.strftime("%Y-%m"))
        months.reverse()

        # Revenue trend query
        revenue_query = (
            select(
                Booking.start_date,
                func.sum(Booking.total_payout_vnd).label("monthly_revenue"),
                func.count(Booking.id).label("monthly_bookings"),
            )
            .where(
                and_(
                    Booking.start_date
                    >= (end_date - timedelta(days=months_back * 30)).strftime(
                        "%Y-%m-%d"
                    ),
                    Booking.status.in_(["confirmed", "checked_in", "checked_out"]),
                )
            )
            .group_by(
                func.substr(Booking.start_date, 1, 7)  # Group by YYYY-MM
            )
            .order_by(func.substr(Booking.start_date, 1, 7))
        )

        # Apply property filtering
        revenue_query = self.apply_property_filter(revenue_query, "property_id")

        # Expense trend query
        expense_query = (
            select(Expense.month, func.sum(Expense.amount).label("monthly_expenses"))
            .where(
                Expense.month
                >= (end_date - timedelta(days=months_back * 30)).strftime("%Y-%m")
            )
            .group_by(Expense.month)
            .order_by(Expense.month)
        )

        # Apply property filtering
        expense_query = self.apply_property_filter(expense_query, "property_id")

        # Execute queries
        revenue_results = self.db.exec(revenue_query).all()
        expense_results = self.db.exec(expense_query).all()

        # Create data maps
        revenue_map = {}
        booking_map = {}
        for row in revenue_results:
            month = row.start_date[:7]  # Extract YYYY-MM
            revenue_map[month] = row.monthly_revenue or 0
            booking_map[month] = row.monthly_bookings or 0

        expense_map = {}
        for row in expense_results:
            expense_map[row.month] = row.monthly_expenses or 0

        # Build trend arrays
        revenue_trend = []
        expense_trend = []
        booking_trend = []
        profit_trend = []

        for month in months:
            revenue = revenue_map.get(month, 0)
            expense = expense_map.get(month, 0)
            bookings = booking_map.get(month, 0)
            profit = revenue - expense

            revenue_trend.append(revenue)
            expense_trend.append(expense)
            booking_trend.append(bookings)
            profit_trend.append(profit)

        # Calculate growth rates (compare last vs first month)
        revenue_growth = (
            ((revenue_trend[-1] - revenue_trend[0]) / revenue_trend[0] * 100)
            if revenue_trend[0] > 0
            else 0
        )
        expense_growth = (
            ((expense_trend[-1] - expense_trend[0]) / expense_trend[0] * 100)
            if expense_trend[0] > 0
            else 0
        )
        booking_growth = (
            ((booking_trend[-1] - booking_trend[0]) / booking_trend[0] * 100)
            if booking_trend[0] > 0
            else 0
        )

        return {
            "months": months,
            "revenue_trend": revenue_trend,
            "expense_trend": expense_trend,
            "booking_trend": booking_trend,
            "profit_trend": profit_trend,
            "summary": {
                "revenue_growth": round(revenue_growth, 2),
                "expense_growth": round(expense_growth, 2),
                "booking_growth": round(booking_growth, 2),
                "months_analyzed": months_back,
                "period": {"start_month": months[0], "end_month": months[-1]},
            },
        }
