"""
Payment Ledger Routes - Google Sheets Integration
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from auth.auth_service import get_current_user, require_role
from services.google_sheets.models import (
    CashHandoverRequest,
    CashHandoverResponse,
    DashboardData,
    PaymentRequest,
    PaymentResponse,
    PaymentUser,
    PaymentValidation,
    UserRole,
)
from services.google_sheets.service import sheets_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/payments", tags=["Payment Ledger"])

# ============ PAYMENT ROUTES ============


@router.post("/add", response_model=Dict[str, Any])
async def add_payment(
    payment: PaymentRequest, current_user: PaymentUser = Depends(get_current_user)
):
    """
    Add new payment to Google Sheets
    Accessible by: Assistant, Manager, Owner
    """
    try:
        # Validate payment data
        validation_errors = PaymentValidation.validate_payment(payment)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": validation_errors},
            )

        # Prepare payment data
        payment_data = {
            "timestamp": datetime.now().isoformat(),
            "booking_id": payment.booking_id,
            "guest_name": payment.guest_name,
            "amount_due": payment.amount_due,
            "amount_collected": payment.amount_collected,
            "payment_method": payment.payment_method.value,
            "collected_by": payment.collected_by,
            "transaction_id": payment.transaction_id or "",
            "notes": payment.notes or "",
            "status": "completed",
        }

        # Add to Google Sheets
        success = await sheets_service.add_payment(payment_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add payment to Google Sheets",
            )

        return {
            "success": True,
            "message": "Payment added successfully",
            "payment_id": payment.booking_id,
            "timestamp": payment_data["timestamp"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while adding payment",
        )


@router.get("/list", response_model=List[PaymentResponse])
async def list_payments(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    collected_by: Optional[str] = None,
    current_user: PaymentUser = Depends(get_current_user),
):
    """
    Get list of payments with filtering
    Accessible by: Assistant (own payments), Manager, Owner (all payments)
    """
    try:
        # Role-based filtering
        if current_user.role == UserRole.ASSISTANT:
            # Assistants can only see their own payments
            collected_by = current_user.username

        # Get payments from Google Sheets
        payments = await sheets_service.get_payments(
            start_date=start_date, end_date=end_date, collected_by=collected_by
        )

        # Convert to response format
        response_payments = []
        for payment in payments:
            response_payments.append(
                PaymentResponse(
                    timestamp=payment.get("Timestamp", ""),
                    booking_id=payment.get("Booking ID", ""),
                    guest_name=payment.get("Guest Name", ""),
                    amount_due=float(payment.get("Amount Due (VND)", 0)),
                    amount_collected=float(payment.get("Amount Collected (VND)", 0)),
                    payment_method=payment.get("Payment Method", ""),
                    collected_by=payment.get("Collected By", ""),
                    transaction_id=payment.get("Transaction ID", ""),
                    notes=payment.get("Notes", ""),
                    status=payment.get("Status", ""),
                )
            )

        return response_payments

    except Exception as e:
        logger.error(f"Error listing payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payments",
        )


# ============ CASH HANDOVER ROUTES ============


@router.post("/cashflow/handover", response_model=Dict[str, Any])
async def add_cash_handover(
    handover: CashHandoverRequest,
    current_user: PaymentUser = Depends(
        require_role([UserRole.ASSISTANT, UserRole.MANAGER, UserRole.OWNER])
    ),
):
    """
    Record cash handover between roles
    Accessible by: Assistant, Manager, Owner
    """
    try:
        # Get current cash balance
        dashboard_data = await sheets_service.get_dashboard_data()
        current_balance = dashboard_data.get("cash_balance", 0)

        # Prepare cashflow data
        cashflow_data = {
            "timestamp": datetime.now().isoformat(),
            "transaction_type": "handover",
            "from_person": handover.from_person,
            "to_person": handover.to_person,
            "amount": handover.amount,
            "cash_balance": current_balance - handover.amount,
            "description": handover.description,
            "approved_by": handover.approved_by or current_user.username,
            "status": "completed",
        }

        # Add to Google Sheets
        success = await sheets_service.add_cashflow(cashflow_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record cash handover",
            )

        return {
            "success": True,
            "message": "Cash handover recorded successfully",
            "new_balance": cashflow_data["cash_balance"],
            "timestamp": cashflow_data["timestamp"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording cash handover: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while recording handover",
        )


@router.get("/cashflow/list", response_model=List[CashHandoverResponse])
async def list_cashflow(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: PaymentUser = Depends(
        require_role([UserRole.MANAGER, UserRole.OWNER])
    ),
):
    """
    Get cashflow history
    Accessible by: Manager, Owner only
    """
    try:
        # Get cashflow from Google Sheets
        cashflow = await sheets_service.get_cashflow(
            start_date=start_date, end_date=end_date
        )

        # Convert to response format
        response_cashflow = []
        for record in cashflow:
            response_cashflow.append(
                CashHandoverResponse(
                    timestamp=record.get("Timestamp", ""),
                    transaction_type=record.get("Transaction Type", ""),
                    from_person=record.get("From Person", ""),
                    to_person=record.get("To Person", ""),
                    amount=float(record.get("Amount (VND)", 0)),
                    cash_balance=float(record.get("Cash Balance", 0)),
                    description=record.get("Description", ""),
                    approved_by=record.get("Approved By", ""),
                    status=record.get("Status", ""),
                )
            )

        return response_cashflow

    except Exception as e:
        logger.error(f"Error listing cashflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cashflow",
        )


# ============ DASHBOARD ROUTES ============


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    current_user: PaymentUser = Depends(
        require_role([UserRole.MANAGER, UserRole.OWNER])
    ),
):
    """
    Get dashboard metrics and KPIs
    Accessible by: Manager, Owner only
    """
    try:
        dashboard_data = await sheets_service.get_dashboard_data()

        return DashboardData(
            total_collected=dashboard_data.get("total_collected", 0),
            total_due=dashboard_data.get("total_due", 0),
            collection_rate=dashboard_data.get("collection_rate", 0),
            cash_in=dashboard_data.get("cash_in", 0),
            cash_out=dashboard_data.get("cash_out", 0),
            cash_balance=dashboard_data.get("cash_balance", 0),
            total_payments=dashboard_data.get("total_payments", 0),
            total_cashflow=dashboard_data.get("total_cashflow", 0),
            last_updated=dashboard_data.get("last_updated", datetime.now().isoformat()),
        )

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data",
        )


@router.get("/dashboard/revenue-by-period")
async def get_revenue_by_period(
    period: str = "month",  # day, week, month
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: PaymentUser = Depends(
        require_role([UserRole.MANAGER, UserRole.OWNER])
    ),
):
    """
    Get revenue aggregated by time period for charts
    """
    try:
        payments = await sheets_service.get_payments(start_date, end_date)

        # Group by period
        revenue_by_period = {}
        for payment in payments:
            timestamp = payment.get("Timestamp", "")
            if not timestamp:
                continue

            # Parse date and format according to period
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

                if period == "day":
                    key = dt.strftime("%Y-%m-%d")
                elif period == "week":
                    # Get Monday of the week
                    monday = dt - timedelta(days=dt.weekday())
                    key = monday.strftime("%Y-%m-%d")
                else:  # month
                    key = dt.strftime("%Y-%m")

                if key not in revenue_by_period:
                    revenue_by_period[key] = {
                        "period": key,
                        "total_collected": 0,
                        "total_due": 0,
                        "payment_count": 0,
                    }

                revenue_by_period[key]["total_collected"] += float(
                    payment.get("Amount Collected (VND)", 0)
                )
                revenue_by_period[key]["total_due"] += float(
                    payment.get("Amount Due (VND)", 0)
                )
                revenue_by_period[key]["payment_count"] += 1

            except Exception as e:
                logger.warning(f"Error parsing timestamp {timestamp}: {e}")
                continue

        # Sort by period and return as list
        sorted_data = sorted(revenue_by_period.values(), key=lambda x: x["period"])

        return {
            "period_type": period,
            "data": sorted_data,
            "total_periods": len(sorted_data),
        }

    except Exception as e:
        logger.error(f"Error getting revenue by period: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue data",
        )


@router.get("/dashboard/collector-performance")
async def get_collector_performance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: PaymentUser = Depends(
        require_role([UserRole.MANAGER, UserRole.OWNER])
    ),
):
    """
    Get performance metrics by collector
    """
    try:
        payments = await sheets_service.get_payments(start_date, end_date)

        # Group by collector
        collector_performance = {}
        for payment in payments:
            collector = payment.get("Collected By", "Unknown")

            if collector not in collector_performance:
                collector_performance[collector] = {
                    "collector": collector,
                    "total_collected": 0,
                    "total_due": 0,
                    "payment_count": 0,
                    "collection_rate": 0,
                }

            collector_performance[collector]["total_collected"] += float(
                payment.get("Amount Collected (VND)", 0)
            )
            collector_performance[collector]["total_due"] += float(
                payment.get("Amount Due (VND)", 0)
            )
            collector_performance[collector]["payment_count"] += 1

        # Calculate collection rates
        for data in collector_performance.values():
            if data["total_due"] > 0:
                data["collection_rate"] = round(
                    (data["total_collected"] / data["total_due"]) * 100, 2
                )

        # Sort by total collected
        sorted_data = sorted(
            collector_performance.values(),
            key=lambda x: x["total_collected"],
            reverse=True,
        )

        return {"collectors": sorted_data, "total_collectors": len(sorted_data)}

    except Exception as e:
        logger.error(f"Error getting collector performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collector performance",
        )
