"""
ExpenseService - Quản lý chi phí với user-aware permissions
==========================================================

Service này handle tất cả expense operations với:
- User-based permission filtering (expense.create / expense.read)
- Property-level data filtering based on user access
- Expense categorization và vendor management
- Monthly/quarterly reporting với aggregations

Author: AI Assistant
Date: 2025-10-03
"""

from datetime import date, datetime
from typing import Dict, Optional, Any
from sqlmodel import select, func
from fastapi import HTTPException

from .base_service import BaseService
from models import Expense, ExpenseCategory, Property


class ExpenseService(BaseService):
    """
    ExpenseService - Expense management với BaseService integration

    Features:
    - Create/update expenses với user tracking
    - Property-based filtering (chỉ show expenses của properties user có access)
    - Category management và vendor analytics
    - Monthly/quarterly summary reports
    - Permission enforcement: expense.create, expense.read
    """

    def create_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo expense mới với validation và user tracking

        Args:
            expense_data: {
                "amount": int,
                "category_id": int,
                "property_id": Optional[int],
                "building_id": Optional[int],
                "vendor": Optional[str],
                "note": Optional[str],
                "date": str,  # YYYY-MM-DD
                "allocation_method": str = "direct"
            }

        Returns:
            {
                "success": bool,
                "expense_id": int,
                "message": str,
                "expense": dict
            }

        Raises:
            HTTPException: 403 if insufficient permissions
            HTTPException: 400 if validation fails
        """
        # Check permission
        self.require_permission("expense", "create")

        # Validate required fields
        required_fields = ["amount", "category_id", "date"]
        missing_fields = [
            f
            for f in required_fields
            if f not in expense_data or expense_data[f] is None
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}",
            )

        # Validate amount
        if expense_data["amount"] <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        # Validate category exists
        category_query = select(ExpenseCategory).where(
            ExpenseCategory.id == expense_data["category_id"]
        )
        category = self.db.exec(category_query).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Property access validation
        if expense_data.get("property_id"):
            # Check user has access to this property
            property_query = select(Property).where(
                Property.id == expense_data["property_id"]
            )
            property_query = self.apply_property_filter(property_query, "id")
            accessible_property = self.db.exec(property_query).first()
            if not accessible_property:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: Property not in your assigned properties",
                )

        # Parse date và generate month
        try:
            expense_date = datetime.strptime(expense_data["date"], "%Y-%m-%d").date()
            month = expense_date.strftime("%Y-%m")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Create expense object
        expense = Expense(
            amount=expense_data["amount"],
            category_id=expense_data["category_id"],
            property_id=expense_data.get("property_id"),
            building_id=expense_data.get("building_id"),
            vendor=expense_data.get("vendor"),
            note=expense_data.get("note"),
            date=expense_data["date"],
            month=month,
            allocation_method=expense_data.get("allocation_method", "direct"),
            allocation_basis_note=expense_data.get("allocation_basis_note"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        try:
            self.db.add(expense)
            self.db.commit()
            self.db.refresh(expense)

            return {
                "success": True,
                "expense_id": expense.id,
                "message": f"Expense created successfully: {expense.amount:,} VNĐ",
                "expense": {
                    "id": expense.id,
                    "amount": expense.amount,
                    "amount_formatted": f"{expense.amount:,} VNĐ",
                    "category_id": expense.category_id,
                    "property_id": expense.property_id,
                    "vendor": expense.vendor,
                    "date": expense.date,
                    "month": expense.month,
                    "created_at": expense.created_at.isoformat(),
                },
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def list_expenses(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        property_id: Optional[int] = None,
        vendor: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List expenses với filtering và pagination

        Returns:
            {
                "expenses": [...],
                "total_count": int,
                "total_amount": int,
                "filters_applied": {...},
                "pagination": {...}
            }
        """
        # Check permission
        self.require_permission("expense", "read")

        # Build base query với joins
        query = select(
            Expense.id,
            Expense.amount,
            Expense.vendor,
            Expense.note,
            Expense.date,
            Expense.month,
            Expense.allocation_method,
            Expense.created_at,
            ExpenseCategory.name.label("category_name"),
            Property.property_name,
        ).select_from(
            Expense.__table__.join(
                ExpenseCategory.__table__, Expense.category_id == ExpenseCategory.id
            ).outerjoin(Property.__table__, Expense.property_id == Property.id)
        )

        # Apply property filtering (chỉ show expenses của properties user có access)
        query = self.apply_property_filter(query, "property_id")

        # Apply additional filters
        if start_date:
            query = query.where(Expense.date >= start_date.strftime("%Y-%m-%d"))
        if end_date:
            query = query.where(Expense.date <= end_date.strftime("%Y-%m-%d"))
        if category_id:
            query = query.where(Expense.category_id == category_id)
        if property_id:
            query = query.where(Expense.property_id == property_id)
        if vendor:
            query = query.where(Expense.vendor.ilike(f"%{vendor}%"))

        # Count total for pagination
        count_query = select(func.count(), func.sum(Expense.amount)).select_from(
            query.subquery()
        )
        count_result = self.db.exec(count_query).first()
        total_count = count_result[0] if count_result else 0
        total_amount = count_result[1] if count_result and count_result[1] else 0

        # Apply pagination và ordering
        query = query.order_by(Expense.date.desc(), Expense.created_at.desc())
        query = query.limit(limit).offset(offset)

        # Execute query
        results = self.db.exec(query).all()

        # Format results
        expenses = []
        for row in results:
            expenses.append(
                {
                    "id": row.id,
                    "amount": row.amount,
                    "amount_formatted": f"{row.amount:,} VNĐ",
                    "vendor": row.vendor,
                    "note": row.note,
                    "date": row.date,
                    "month": row.month,
                    "allocation_method": row.allocation_method,
                    "category_name": row.category_name,
                    "property_name": row.property_name,
                    "created_at": row.created_at.isoformat()
                    if row.created_at
                    else None,
                }
            )

        return {
            "expenses": expenses,
            "total_count": total_count,
            "total_amount": total_amount,
            "total_amount_formatted": f"{total_amount:,} VNĐ",
            "filters_applied": {
                "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
                "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
                "category_id": category_id,
                "property_id": property_id,
                "vendor": vendor,
            },
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count,
            },
        }

    def summary_by_property(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Expense summary grouped by property với aggregations

        Returns:
            {
                "summary": {
                    "total_properties": int,
                    "total_expenses": int,
                    "total_amount": int,
                    "avg_expense_per_property": float
                },
                "properties": [
                    {
                        "property_id": int,
                        "property_name": str,
                        "expense_count": int,
                        "total_amount": int,
                        "categories": [...],
                        "vendors": [...]
                    }
                ]
            }
        """
        # Check permission
        self.require_permission("expense", "read")

        # Build aggregation query
        query = (
            select(
                Expense.property_id,
                Property.property_name,
                func.count(Expense.id).label("expense_count"),
                func.sum(Expense.amount).label("total_amount"),
                func.avg(Expense.amount).label("avg_amount"),
                func.min(Expense.date).label("first_expense"),
                func.max(Expense.date).label("last_expense"),
            )
            .select_from(
                Expense.__table__.outerjoin(
                    Property.__table__, Expense.property_id == Property.id
                )
            )
            .group_by(Expense.property_id, Property.property_name)
        )

        # Apply property filtering
        query = self.apply_property_filter(query, "property_id")

        # Apply date filters
        if start_date:
            query = query.where(Expense.date >= start_date.strftime("%Y-%m-%d"))
        if end_date:
            query = query.where(Expense.date <= end_date.strftime("%Y-%m-%d"))

        # Execute query
        results = self.db.exec(query).all()

        # Calculate summary
        total_properties = len(results)
        total_expenses = sum(r.expense_count for r in results)
        total_amount = sum(r.total_amount for r in results)
        avg_expense_per_property = (
            total_amount / total_properties if total_properties > 0 else 0
        )

        # Format properties
        properties = []
        for row in results:
            properties.append(
                {
                    "property_id": row.property_id,
                    "property_name": row.property_name or "Unassigned",
                    "expense_count": row.expense_count,
                    "total_amount": row.total_amount,
                    "amount_formatted": f"{row.total_amount:,} VNĐ",
                    "avg_amount": float(row.avg_amount) if row.avg_amount else 0,
                    "first_expense": row.first_expense,
                    "last_expense": row.last_expense,
                }
            )

        # Sort by total amount (descending)
        properties.sort(key=lambda x: x["total_amount"], reverse=True)

        return {
            "summary": {
                "total_properties": total_properties,
                "total_expenses": total_expenses,
                "total_amount": total_amount,
                "total_amount_formatted": f"{total_amount:,} VNĐ",
                "avg_expense_per_property": avg_expense_per_property,
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d")
                    if start_date
                    else None,
                    "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
                },
            },
            "properties": properties,
        }
