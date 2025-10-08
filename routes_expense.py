# ---- Extra charges endpoints ----
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import ExtraCharge

extra_charges_router = APIRouter(prefix="/extra_charges", tags=["extra_charges"])


@extra_charges_router.get("")
def list_extra_charges(property_id: int, session: Session = Depends(get_session)):
    rows = session.exec(
        select(ExtraCharge)
        .where(ExtraCharge.property_id == property_id)
        .order_by(ExtraCharge.charge_month.desc())
    ).all()
    return rows


@extra_charges_router.post("")
def create_extra_charge(payload: ExtraCharge, session: Session = Depends(get_session)):
    session.add(payload)
    session.commit()
    session.refresh(payload)
    return payload


@extra_charges_router.delete("/{charge_id}")
def delete_extra_charge(charge_id: int, session: Session = Depends(get_session)):
    row = session.get(ExtraCharge, charge_id)
    if not row:
        raise HTTPException(404, "Not found")
    session.delete(row)
    session.commit()
    return {"ok": True}


from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

# và db.py ở gốc, có hàm get_session
from db import get_session

# dự án của anh có models.py ở gốc
from models import Expense, ExpenseAllocation, RecurringExpense

# --- 2 router public mà main.py sẽ import ---
router = APIRouter(prefix="/expenses", tags=["expenses"])
rec_router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"])

# ===== Expenses CRUD =====


@router.get("")
def list_expenses(
    month: str | None = None,
    building_id: int | None = None,
    property_id: int | None = None,
    session: Session = Depends(get_session),
):
    q = select(Expense)
    if month:
        q = q.where(Expense.month == month)
    if building_id:
        q = q.where(Expense.building_id == building_id)
    if property_id:
        q = q.where(Expense.property_id == property_id)
    q = q.order_by(Expense.date)
    return session.exec(q).all()


@router.post("")
def create_expense(payload: Expense, session: Session = Depends(get_session)):
    payload.updated_at = datetime.utcnow()
    session.add(payload)
    session.commit()
    session.refresh(payload)
    return payload


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, session: Session = Depends(get_session)):
    row = session.get(Expense, expense_id)
    if not row:
        raise HTTPException(404, "Not found")
    session.delete(row)
    session.commit()
    return {"ok": True}


# ===== Recurring templates =====


@rec_router.get("")
def list_recurring(session: Session = Depends(get_session)):
    return session.exec(
        select(RecurringExpense).where(RecurringExpense.is_active == 1)
    ).all()


@rec_router.post("")
def create_recurring(
    payload: RecurringExpense, session: Session = Depends(get_session)
):
    session.add(payload)
    session.commit()
    session.refresh(payload)
    return payload


@rec_router.post("/run")
def run_recurring(month: str, session: Session = Depends(get_session)):
    rows = session.exec(
        select(RecurringExpense).where(RecurringExpense.is_active == 1)
    ).all()
    created = 0
    for r in rows:
        if month < r.start_month:
            continue
        if r.end_month and month > r.end_month:
            continue
        e = Expense(
            date=f"{month}-01",
            month=month,
            category_id=r.category_id,
            amount=r.amount,
            vendor=r.vendor,
            note=r.note,
            building_id=r.building_id,
            property_id=r.property_id,
            allocation_method=r.allocation_method,
            allocation_basis_note=f"recurring #{r.id}",
        )
        session.add(e)
        session.commit()
        created += 1
    return {"created": created}


# ===== Allocation (tạm dùng số liệu giả để test) =====


@router.post("/allocate")
def allocate(
    month: str,
    building_id: int | None = None,
    method_override: str | None = None,
    session: Session = Depends(get_session),
):
    # tránh lỗi nếu anh chưa thêm hàm trong utils.py
    try:
        from utils import (
            get_properties_stats,
        )  # -> list[{"property_id", "available_nights", "sold_nights"}]
    except Exception as e:
        raise HTTPException(500, f"Thiếu utils.get_properties_stats(): {e}")

    stats = get_properties_stats(month, building_id)
    if not stats:
        raise HTTPException(400, "No stats available for allocation")

    total_props = len(stats)
    total_avail = sum(s.get("available_nights", 0) for s in stats)
    total_sold = sum(s.get("sold_nights", 0) for s in stats)

    q = select(Expense).where(Expense.month == month, Expense.property_id is None)
    if building_id:
        q = q.where(Expense.building_id == building_id)
    rows = session.exec(q).all()

    # xóa phân bổ cũ
    for e in rows:
        session.exec(f"DELETE FROM expense_allocations WHERE expense_id={e.id}")
        session.commit()

        base = e.amount
        method = (method_override or e.allocation_method) or "per_occupied_night"
        for s in stats:
            if method == "per_property":
                share = base / (total_props or 1)
            elif method == "per_available_night":
                denom = total_avail or 1
                share = base * (s.get("available_nights", 0) / denom)
            else:  # per_occupied_night (default)
                denom = total_sold or 1
                share = base * (s.get("sold_nights", 0) / denom)
            alloc = ExpenseAllocation(
                expense_id=e.id,
                property_id=s["property_id"],
                month=month,
                allocated_amount=int(round(share)),
            )
            session.add(alloc)
        session.commit()

    return {"allocated_expenses": len(rows)}


# ---- AUX endpoints: categories / buildings / properties ----
from models import Building  # 2 model này đã có trong models.py của anh
from models import ExpenseCategory, Property

aux = APIRouter(prefix="/expense-aux", tags=["expense-aux"])


@aux.get("/categories")
def categories():
    with get_session() as session:
        rows = session.exec(
            select(ExpenseCategory).order_by(ExpenseCategory.name)
        ).all()
        return [{"id": r.id, "name": r.name} for r in rows]


@aux.get("/buildings")
def buildings(session: Session = Depends(get_session)):
    rows = session.exec(select(Building).order_by(Building.id)).all()
    return [{"id": r.id, "name": r.building_name} for r in rows]


@aux.get("/properties")
def properties(session: Session = Depends(get_session)):
    rows = session.exec(select(Property).order_by(Property.id)).all()
    return [
        {"id": r.id, "name": r.property_name, "building_id": r.building_id}
        for r in rows
    ]
