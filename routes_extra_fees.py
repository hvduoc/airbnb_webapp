from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import Expense

extra_fees_router = APIRouter(prefix="/extra_fees", tags=["extra_fees"])


@extra_fees_router.post("")
def create_extra_fee(payload: dict, session: Session = Depends(get_session)):
    with session:
        property_id = payload.get("property_id")
        month = payload.get("month")
        electricity = payload.get("electricity")
        water = payload.get("water")
        note = payload.get("note")

        if not property_id or not month or electricity is None or water is None:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Create electricity expense
        electricity_expense = Expense(
            property_id=property_id,
            month=month,
            category_id=1,  # Assuming 1 is the category_id for electricity
            amount=electricity,
            note=note,
        )
        session.add(electricity_expense)

        # Create water expense
        water_expense = Expense(
            property_id=property_id,
            month=month,
            category_id=2,  # Assuming 2 is the category_id for water
            amount=water,
            note=note,
        )
        session.add(water_expense)

        session.commit()
        return {"message": "Extra fees added successfully"}


@extra_fees_router.get("")
def list_extra_fees(
    property_id: int, month: str, session: Session = Depends(get_session)
):
    with session:
        expenses = session.exec(
            select(Expense).where(
                Expense.property_id == property_id,
                Expense.month == month,
                Expense.category_id.in_([1, 2]),  # Filter for electricity and water
            )
        ).all()
        return expenses


@extra_fees_router.delete("/{expense_id}")
def delete_extra_fee(expense_id: int, session: Session = Depends(get_session)):
    with session:
        expense = session.get(Expense, expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        session.delete(expense)
        session.commit()
        return {"message": "Expense deleted successfully"}
