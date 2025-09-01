from fastapi import FastAPI, Request, UploadFile, File, Query, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session
from sqlalchemy import or_, not_, case
import pandas as pd
from datetime import datetime, date, timedelta
from calendar import monthrange
from collections import defaultdict
from typing import Optional, List   # thay dòng cũ có Optional
from fastapi import Query
import uuid
from sqlalchemy.sql import func
import os, asyncio
from dotenv import load_dotenv
load_dotenv()  # <-- để tự động nạp .env
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import math
from sqlalchemy import func

from db import init_db, get_session
from models import Booking, Property, Channel, ImportLog, Building, Salesperson
from utils import (
    VN_HEADERS, parse_date_mixed, parse_vnd,
    parse_building_and_unit, building_code_from_name, unit_short_from_unit_number_auto,
    pick  # <--- thêm
)
from fastapi.responses import StreamingResponse
from io import BytesIO
from models import Salesperson
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse
import io, zipfile
import httpx
from fastapi.responses import StreamingResponse, HTMLResponse
from urllib.parse import urlencode

from fastapi import Request, Form
from models import Building, Property
from db import get_session
from sqlmodel import select, func





scheduler = None
# --- Added: Compute total number of properties dynamically ---
def _get_total_properties():
    try:
        from webapp.models import Property
        from webapp.db import SessionLocal
        with SessionLocal() as db:
            return db.query(Property).count()
    except Exception as e:
        print("WARNING: Cannot compute total properties dynamically:", e)
        return 0

def get_next_run_time():
    try:
        if scheduler:
            jobs = scheduler.get_jobs()
            if jobs:
                return jobs[0].next_run_time  # timezone-aware
    except Exception:
        pass
    return None



app = FastAPI(title="CSV Ingest (Airbnb)")
templates = Jinja2Templates(directory="templates")
# --- Jinja filters: định dạng ngày DD/MM/YYYY và tháng MM/YYYY ---
def vn_date(v):
    if not v:
        return ""
    try:
        return v.strftime("%d/%m/%Y")
    except Exception:
        return str(v)

def vn_month(v):
    if not v:
        return ""
    try:
        return v.strftime("%m/%Y")
    except Exception:
        return str(v)

def vnd(v):
    try:
        return f"{int(v):,}"
    except Exception:
        return "0"

templates.env.filters["vn_date"] = vn_date
templates.env.filters["vn_month"] = vn_month
templates.env.filters["vnd"] = vnd

def vn_dt(v):
    if not v:
        return ""
    try:
        return v.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(v)

templates.env.filters["vn_dt"] = vn_dt


@app.on_event("startup")
def on_startup():
    init_db()
    with get_session() as session:
        airbnb = session.exec(select(Channel).where(Channel.channel_name == "Airbnb")).first()
        if not airbnb:
            session.add(Channel(channel_name="Airbnb")); session.commit()
        offline = session.exec(select(Channel).where(Channel.channel_name == "Offline")).first()
        if not offline:
            session.add(Channel(channel_name="Offline")); session.commit()

    # ---- LỊCH HẰNG NGÀY ----
    global scheduler
    if os.getenv("AIRBNB_COOKIE", "").strip():
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")
        scheduler.add_job(lambda: asyncio.create_task(_trigger_ingest_page1()),
                          CronTrigger(hour=2, minute=0))  # chỉnh giờ nếu muốn
        scheduler.start()
        print("[Scheduler] Daily ingest scheduled at 02:00 Asia/Ho_Chi_Minh")
    else:
        print("[Scheduler] Skip: AIRBNB_COOKIE chưa thiết lập")

@app.get("/airbnb/ingest/run-now")
def run_now():
    # mở trang ingest trang 1 (limit 40) và hiển thị kết quả ngay
    return RedirectResponse(
        url="/airbnb/ingest?page_from=1&page_to=1&limit=40",
        status_code=303
    )

        
@app.get("/airbnb/csv-link")
def airbnb_csv_link(page: int = 1, limit: int = 40):
    offset = (page - 1) * limit
    base = "https://www.airbnb.com.vn/api/v2/download_reservations"
    params = {
        "_format":"for_remy","_limit":str(limit),"_offset":str(offset),
        "collection_strategy":"for_reservations_list","sort_field":"start_date","sort_order":"desc",
        "status":"accepted,request,canceled","page":str(page),
        "key":"d306zoyjsyarp7ifhu67rjxn52tv0t20","currency":"VND","locale":"vi",
    }
    qs = urlencode(params, safe=",")
    return RedirectResponse(url=f"{base}?{qs}")

async def _trigger_ingest_page1():
    """Gọi ingest trang 1 (limit 40) qua endpoint nội bộ."""
    base = os.getenv("SELF_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    url = f"{base}/airbnb/ingest?page_from=1&page_to=1&limit=40"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.get(url)
            print(f"[DailyIngest] {url} -> {r.status_code}")
    except Exception as e:
        print(f"[DailyIngest] error: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, msg: Optional[str] = None, success: Optional[bool] = None):
    last_ingest = None
    with get_session() as session:
        last_ingest = session.exec(
            select(ImportLog)
            .where(ImportLog.filename.ilike("airbnb:%"))
            .order_by(ImportLog.finished_at.desc())
        ).first()
    next_run = get_next_run_time()
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "msg": msg, "success": success,
        "ingest_last": last_ingest,
        "ingest_next": next_run,
    })


@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, files: List[UploadFile] = File(...)):
    started_all = datetime.utcnow()
    summaries = []
    total_inserted = 0
    total_updated = 0

    try:
        with get_session() as session:
            airbnb = session.exec(select(Channel).where(Channel.channel_name == "Airbnb")).first()

            for up in files:
                filename = up.filename or "uploaded.csv"
                rows_inserted = 0
                rows_updated = 0
                try:
                    content = await up.read()
                    df = pd.read_csv(pd.io.common.BytesIO(content))

                    for _, row in df.iterrows():
                        cc_col = pick(df, "confirmation_code")
                        if not cc_col:
                            continue
                        cc = str(row.get(cc_col, "")).strip()
                        if not cc:
                            continue

                        status_col = pick(df, "status")
                        status = str(row.get(status_col, "")).strip() if status_col else None

                        gname_col = pick(df, "guest_name")
                        guest_name = str(row.get(gname_col, "")).strip() if gname_col else None

                        gcontact_col = pick(df, "guest_contact")
                        guest_contact = str(row.get(gcontact_col, "")).strip() if gcontact_col else None

                        st_col = pick(df, "start_date")
                        en_col = pick(df, "end_date")
                        bk_col = pick(df, "booking_date")
                        start_date = parse_date_mixed(row.get(st_col)) if st_col else None
                        end_date = parse_date_mixed(row.get(en_col)) if en_col else None
                        booking_date = parse_date_mixed(row.get(bk_col)) if bk_col else None

                        nights_col = pick(df, "num_nights")
                        num_nights = row.get(nights_col) if nights_col else None
                        try:
                            num_nights = int(num_nights) if pd.notna(num_nights) else None
                        except Exception:
                            num_nights = None
                        # tự tính nếu thiếu
                        if start_date and end_date:
                            calc = (end_date - start_date).days
                            if calc > 0:
                                num_nights = int(calc)

                        ad_col = pick(df, "num_adults")
                        ch_col = pick(df, "num_children")
                        inf_col = pick(df, "num_infants")
                        num_adults = int(row.get(ad_col)) if ad_col and pd.notna(row.get(ad_col)) else None
                        num_children = int(row.get(ch_col)) if ch_col and pd.notna(row.get(ch_col)) else None
                        num_infants = int(row.get(inf_col)) if inf_col and pd.notna(row.get(inf_col)) else None

                        lst_col = pick(df, "listing")
                        listing = str(row.get(lst_col, "")).strip() if lst_col else None

                        inc_col = pick(df, "income")
                        income_vnd = parse_vnd(row.get(inc_col)) if inc_col else None

                        # --- building / property short ---
                        bld_name, unit_num = parse_building_and_unit(listing)
                        bld_code = building_code_from_name(bld_name) if bld_name else None
                        unit_short = unit_short_from_unit_number_auto(unit_num) if unit_num else None
                        prop_short = f"{bld_code}-{unit_short}" if (bld_code and unit_short) else None

                        # upsert building
                        building = None
                        if bld_name:
                            building = session.exec(select(Building).where(Building.building_name == bld_name)).first()
                            if not building:
                                building = Building(building_name=bld_name, building_code=bld_code)
                                session.add(building); session.commit(); session.refresh(building)

                        # upsert property
                        prop = None
                        if listing:
                            # Tìm theo airbnb_name nếu có
                            prop = session.exec(select(Property).where(Property.airbnb_name == listing)).first()

                            # Nếu không có, thử tìm theo property_name
                            if not prop:
                                prop = session.exec(select(Property).where(Property.property_name == listing)).first()

                            if not prop:
                                prop = Property(
                                    property_name=prop_short or listing,
                                    airbnb_name=listing,
                                    building_id=building.id if building else None,
                                    building_name=bld_name,
                                    building_code=bld_code,
                                    unit_number=unit_num,
                                    unit_short=unit_short,
                                    property_short=prop_short
                                )
                                session.add(prop); session.commit(); session.refresh(prop)
                            else:
                                updated = False
                                if (not prop.building_id) and building: prop.building_id = building.id; updated = True
                                if (not prop.building_name) and bld_name: prop.building_name = bld_name; updated = True
                                if (not prop.building_code) and bld_code: prop.building_code = bld_code; updated = True
                                if (not prop.unit_number) and unit_num: prop.unit_number = unit_num; updated = True
                                if (not prop.unit_short) and unit_short: prop.unit_short = unit_short; updated = True
                                if (not prop.property_short) and prop_short: prop.property_short = prop_short; updated = True
                                if updated: session.add(prop); session.commit()

                        # upsert booking
                        existing = session.exec(select(Booking).where(Booking.confirmation_code == cc)).first()
                        if existing:
                            existing.property_id = prop.id if prop else existing.property_id
                            existing.channel_id = airbnb.id if airbnb else existing.channel_id
                            existing.start_date = start_date or existing.start_date
                            existing.end_date = end_date or existing.end_date
                            # cập nhật num_nights nếu tính được
                            if num_nights is not None: existing.num_nights = num_nights
                            if num_adults is not None: existing.num_adults = num_adults
                            if num_children is not None: existing.num_children = num_children
                            if num_infants is not None: existing.num_infants = num_infants
                            existing.booking_date = booking_date or existing.booking_date
                            existing.status = status or existing.status
                            if income_vnd is not None: existing.total_payout_vnd = income_vnd
                            existing.guest_name = guest_name or existing.guest_name
                            existing.guest_contact = guest_contact or existing.guest_contact
                            existing.listing_raw = listing or existing.listing_raw
                            session.add(existing)
                            rows_updated += 1
                        else:
                            b = Booking(
                                confirmation_code=cc,
                                property_id=prop.id if prop else None,
                                channel_id=airbnb.id if airbnb else None,
                                start_date=start_date,
                                end_date=end_date,
                                num_nights=num_nights,
                                num_adults=num_adults,
                                num_children=num_children,
                                num_infants=num_infants,
                                booking_date=booking_date,
                                status=status,
                                total_payout_vnd=income_vnd,
                                guest_name=guest_name,
                                guest_contact=guest_contact,
                                listing_raw=listing,
                            )
                            session.add(b)
                            rows_inserted += 1

                    session.commit()

                    # log cho từng file
                    log = ImportLog(
                        filename=filename,
                        started_at=started_all,
                        finished_at=datetime.utcnow(),
                        status="success",
                        rows_inserted=rows_inserted,
                        rows_updated=rows_updated,
                        message=f"Imported {rows_inserted} inserted, {rows_updated} updated."
                    )
                    session.add(log); session.commit()

                    summaries.append(f"{filename}: {rows_inserted} mới, {rows_updated} cập nhật")
                    total_inserted += rows_inserted
                    total_updated += rows_updated

                except Exception as e:
                    # log lỗi cho file này nhưng tiếp tục các file khác
                    log = ImportLog(
                        filename=filename,
                        started_at=started_all,
                        finished_at=datetime.utcnow(),
                        status="error",
                        rows_inserted=0,
                        rows_updated=0,
                        message=str(e)
                    )
                    session.add(log); session.commit()
                    summaries.append(f"{filename}: lỗi {e}")

        msg = f"Đã xử lý {len(files)} tệp. Tổng: {total_inserted} mới, {total_updated} cập nhật.\n" + " · ".join(summaries)
        return templates.TemplateResponse("upload.html", {"request": request, "msg": msg, "success": True})

    except Exception as e:
        return templates.TemplateResponse("upload.html", {"request": request, "msg": f"Lỗi: {e}", "success": False})


# 1. HIỂN THỊ FORM THÊM MỚI (ĐẶT LÊN ĐẦU TIÊN)

@app.get("/bookings/new", response_class=HTMLResponse)
async def show_add_booking_form(
    request: Request,
    channel: Optional[str] = Query(None),      # ví dụ: ?channel=Offline
    channel_id: Optional[int] = Query(None),   # ví dụ: ?channel_id=2
    offline: Optional[bool] = Query(False)     # ví dụ: ?offline=1
):
    """Hiển thị form để thêm booking mới, hỗ trợ chọn sẵn kênh."""
    with get_session() as session:
        properties = session.exec(select(Property).order_by(Property.property_name)).all()
        channels = session.exec(select(Channel).order_by(Channel.channel_name)).all()
        salespeople = session.exec(select(Salesperson).where(Salesperson.is_active == True)).all()

        # Xác định channel mặc định
        default_channel_id = None
        if channel_id:
            default_channel_id = channel_id
        elif channel:
            ch = session.exec(select(Channel).where(Channel.channel_name.ilike(channel))).first()
            default_channel_id = ch.id if ch else None
        elif offline:
            ch = session.exec(select(Channel).where(Channel.channel_name == "Offline")).first()
            default_channel_id = ch.id if ch else None

        return templates.TemplateResponse("add_booking.html", {
            "request": request,
            "properties": properties,
            "channels": channels,
            "salespeople": salespeople,
            "default_channel_id": default_channel_id,  # <--- truyền qua template
        })
        
@app.post("/bookings/new")
async def create_booking(
    request: Request,
    property_id: int = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    total_payout_vnd: int = Form(...),
    channel_id: int = Form(...),
    guest_name: Optional[str] = Form(None),
    guest_contact: Optional[str] = Form(None),
    confirmation_code: Optional[str] = Form(None),
    salesperson_id: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
):
    """Xử lý dữ liệu từ form và lưu vào database."""
    with get_session() as session:
        if not confirmation_code:
            confirmation_code = f"OFF-{uuid.uuid4().hex[:8].upper()}"

        num_nights = (end_date - start_date).days

        # ✅ Lấy thông tin căn hộ
        prop = session.get(Property, property_id)
        property_short = prop.property_short if prop else None
        airbnb_name = prop.airbnb_name.strip() if prop and prop.airbnb_name else ""

        # ✅ Chỉ hiển thị dòng dưới nếu khác dòng trên
        listing_name = airbnb_name if airbnb_name and airbnb_name != property_short else None


        new_booking = Booking(
            property_id=property_id,
            channel_id=channel_id,
            confirmation_code=confirmation_code,
            start_date=start_date,
            end_date=end_date,
            num_nights=num_nights,
            total_payout_vnd=total_payout_vnd,
            guest_name=guest_name,
            guest_contact=guest_contact,
            status="xác nhận",
            booking_date=date.today(),
            salesperson_id=salesperson_id,
            notes=notes,
            listing_raw=listing_name,  # ✅ Chỉ hiển thị nếu khác tên ngắn
        )

        session.add(new_booking)
        session.commit()

    return RedirectResponse(url="/bookings", status_code=303)
 

@app.get("/bookings/{booking_id}/edit", response_class=HTMLResponse)
async def edit_booking_form(request: Request, booking_id: int):
    with get_session() as session:
        booking = session.get(Booking, booking_id)
        if not booking:
            return RedirectResponse("/bookings", status_code=302)

        properties = session.exec(select(Property).order_by(Property.property_name)).all()
        channels = session.exec(select(Channel).order_by(Channel.channel_name)).all()
        salespeople = session.exec(select(Salesperson).where(Salesperson.is_active == True)).all()

        return templates.TemplateResponse("edit_booking.html", {
            "request": request,
            "booking": booking,
            "properties": properties,
            "channels": channels,
            "salespeople": salespeople
        })
@app.post("/bookings/{booking_id}/edit")
async def update_booking(
    booking_id: int,
    property_id: int = Form(...),
    channel_id: int = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    total_payout_vnd: int = Form(...),
    guest_name: str = Form(None),
    guest_contact: str = Form(None),
    salesperson_id: Optional[int] = Form(None),
    notes: Optional[str] = Form(None)
):
    with get_session() as session:
        booking = session.get(Booking, booking_id)
        if not booking:
            return RedirectResponse("/bookings", status_code=302)

        booking.property_id = property_id
        booking.channel_id = channel_id
        booking.start_date = start_date
        booking.end_date = end_date
        booking.num_nights = (end_date - start_date).days
        booking.total_payout_vnd = total_payout_vnd
        booking.guest_name = guest_name
        booking.guest_contact = guest_contact
        booking.salesperson_id = salesperson_id
        booking.notes = notes

        session.add(booking)
        session.commit()

        return RedirectResponse("/bookings", status_code=302)

@app.post("/bookings/{booking_id}/delete")
async def delete_booking(booking_id: int):
    with get_session() as session:
        booking = session.get(Booking, booking_id)
        if booking:
            session.delete(booking)
            session.commit()
    return RedirectResponse("/bookings", status_code=303)

@app.get("/salespeople", response_class=HTMLResponse)
async def manage_salespeople(request: Request):
    """Hiển thị trang quản lý nhân viên sale."""
    with get_session() as session:
        salespeople = session.exec(select(Salesperson).order_by(Salesperson.name)).all()
        return templates.TemplateResponse("salespeople.html", {
            "request": request,
            "salespeople": salespeople
        })

@app.post("/salespeople/new")
async def handle_add_salesperson(
    name: str = Form(...),
    email: Optional[str] = Form(None), # Thêm email
    phone: Optional[str] = Form(None), # Thêm phone
    commission_rate_pct: float = Form(...)
):
    """Xử lý thêm nhân viên sale mới."""
    with get_session() as session:
        commission_rate = commission_rate_pct / 100.0
        
        new_salesperson = Salesperson(
            name=name,
            email=email,
            phone=phone,
            commission_rate=commission_rate,
            is_active=True
        )
        session.add(new_salesperson)
        session.commit()
        
    return RedirectResponse(url="/salespeople", status_code=303)

# 2. HIỂN THỊ CHI TIẾT 1 BOOKING (ĐẶT SAU /new)
@app.get("/bookings/{booking_id}", response_class=HTMLResponse)
async def get_booking_detail(request: Request, booking_id: int):
    """
    Handles displaying the detailed view for a single booking.
    """
    with get_session() as session:
        booking = session.get(Booking, booking_id)

        if not booking:
            return templates.TemplateResponse("upload.html", {
                "request": request,
                "msg": f"Không tìm thấy đặt phòng với ID {booking_id}.",
                "success": False
            })

        prop = session.get(Property, booking.property_id) if booking.property_id else None
        chan = session.get(Channel, booking.channel_id) if booking.channel_id else None

        booking_vm = {
            "id": booking.id, # Thêm ID để có thể dùng trong template nếu cần
            "confirmation_code": booking.confirmation_code,
            "listing_raw": booking.listing_raw,
            "building_name": prop.building_name if prop else None,
            "unit_number": prop.unit_number if prop else None,
            "unit_short": prop.unit_short if prop else None,
            "property_short": prop.property_short if prop else None,
            "booking_date": booking.booking_date,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "num_nights": booking.num_nights,
            "guest_name": booking.guest_name,
            "guest_contact": booking.guest_contact,
            "num_adults": booking.num_adults,
            "num_children": booking.num_children,
            "num_infants": booking.num_infants,
            "status": booking.status,
            "total_payout_vnd": booking.total_payout_vnd,
            "channel_name": chan.channel_name if chan else "N/A",
        }

        return templates.TemplateResponse("booking_detail.html", {
            "request": request,
            "b": booking_vm
        })

# 3. HIỂN THỊ DANH SÁCH BOOKING (ROUTE GỐC)
@app.get("/bookings", response_class=HTMLResponse)
async def list_bookings(
    request: Request,
    start: Optional[str] = None,
    end: Optional[str] = None,
    status: Optional[str] = None,
    channel: Optional[str] = None,
    building: Optional[str] = None,
    property_name: Optional[str] = Query(None, alias="property"),
    p: int = Query(1, ge=1),                            # <-- trang hiện tại
    page_size: int = Query(50, ge=10, le=200),         # <-- số dòng / trang
):
    start_date = parse_date_mixed(start) if start else None
    end_date   = parse_date_mixed(end)   if end else None

    with get_session() as session:
        # lookup maps
        ch_map = {c.id: c.channel_name for c in session.exec(select(Channel)).all()}
        props = {p.id: p for p in session.exec(select(Property)).all()}

        # ---- build filterable list of property_ids theo building / property ----
        matched_prop_ids = None
        if building:
            matched_prop_ids = [
                pid for pid, p in props.items()
                if p and p.building_name and building.lower() in p.building_name.lower()
            ]

        if property_name:
            ids_by_prop = [
                pid for pid, p in props.items()
                if p and (
                    (p.property_short and property_name.lower() in p.property_short.lower())
                    or (p.property_name and property_name.lower() in p.property_name.lower())
                )
            ]
            matched_prop_ids = ids_by_prop if matched_prop_ids is None else list(set(matched_prop_ids).intersection(ids_by_prop))

        # ---- base WHERE ----
        where_clauses = []
        if status:
            where_clauses.append(Booking.status.ilike(f"%{status}%"))

        if channel:
            channel_ids = [cid for cid, name in ch_map.items() if name and channel.lower() in name.lower()]
            if channel_ids:
                where_clauses.append(Booking.channel_id.in_(channel_ids))
            else:
                where_clauses.append(Booking.channel_id == -1)

        if matched_prop_ids is not None:
            if matched_prop_ids:
                where_clauses.append(Booking.property_id.in_(matched_prop_ids))
            else:
                where_clauses.append(Booking.property_id == -1)

        if start_date:
            where_clauses.append(Booking.end_date >= start_date)
        if end_date:
            where_clauses.append(Booking.start_date <= end_date)

        # ---- count total (để tính tổng trang) ----
        total_q = select(func.count()).select_from(Booking)
        for cond in where_clauses:
            total_q = total_q.where(cond)
        total_rows = session.exec(total_q).one()

        # ---- page clamp + offset/limit ----
        pages = max(1, math.ceil(total_rows / page_size))
        page = min(max(1, p), pages)
        offset = (page - 1) * page_size

        # ---- fetch page data ----
        q = select(Booking)
        for cond in where_clauses:
            q = q.where(cond)
        q = q.order_by(Booking.id.desc()).offset(offset).limit(page_size)

        results = session.exec(q).all()

        # ---- build view model ----
        bookings_vm = []
        for r in results:
            total_vnd = int(r.total_payout_vnd or 0)
            pinfo = props.get(r.property_id)
            bookings_vm.append({
                "id": r.id,
                "confirmation_code": r.confirmation_code,
                "listing_raw": r.listing_raw,
                "property_short": (pinfo.property_short if pinfo else None),
                "start_date": vn_date(r.start_date),
                "end_date": vn_date(r.end_date),
                "num_nights": r.num_nights,
                "status": r.status,
                "total_payout_vnd": total_vnd,
                "channel_name": ch_map.get(r.channel_id),
                "guest_name": r.guest_name,
                "guest_contact": r.guest_contact,
                "num_adults": r.num_adults,
                "num_children": r.num_children,
                "num_infants": r.num_infants,
                "booking_date": vn_date(r.booking_date),
            })

        # danh sách tòa nhà cho filter
        all_buildings = session.exec(select(Building.building_name).distinct()).all()

    pagination = {
        "page": page,
        "page_size": page_size,
        "total": total_rows,
        "pages": pages,
        "start": (offset + 1) if total_rows else 0,
        "end": offset + len(bookings_vm),
    }

    return templates.TemplateResponse("bookings.html", {
        "request": request,
        "bookings": bookings_vm,
        "start": start_date,
        "end": end_date,
        "status": status,
        "channel": channel,
        "building": building,
        "property": property_name,
        "all_buildings": all_buildings,
        "pagination": pagination,
    })


    
def month_key(d: date) -> date:
    return date(d.year, d.month, 1)

def days_in_month(dt: date) -> int:
    return monthrange(dt.year, dt.month)[1]

# Trong file main.py

def compute_monthly_report(start_date: date, end_date: date, group_by: str):
    """
    Hàm tính toán báo cáo tháng, gồm:
    - Bảng tổng hợp theo group_by (property/building/channel/salesperson)
    - KPI totals
    - Chart: trend theo tháng + pie "channel_revenue"
    - Bao gồm tất cả căn hộ (kể cả không có booking)
    - Tính thêm: đêm trống (vacant), dự báo doanh thu, doanh thu theo kênh Offline
    """
    with get_session() as session:
        bookings = session.exec(
            select(Booking).where(
                or_(
                    Booking.status.is_(None),
                    not_(Booking.status.ilike("%hủy%"))
                )
            )
        ).all()
        props = {p.id: p for p in session.exec(select(Property)).all()}
        chans = {c.id: c for c in session.exec(select(Channel)).all()}
        sales_map = {s.id: s for s in session.exec(select(Salesperson)).all()}

    results = defaultdict(lambda: {"sold_nights": 0, "revenue": 0.0, "commission": 0.0, "prop_ids": set()})
    monthly_sold = defaultdict(int)
    monthly_rev = defaultdict(float)
    monthly_props_any = defaultdict(set)
    channel_totals = defaultdict(float)
    monthly_offline_rev = defaultdict(float)
    monthly_airbnb_rev = defaultdict(float)


    for b in bookings:
        if not (b.start_date and b.end_date and b.num_nights and b.total_payout_vnd is not None):
            continue

        cur = max(b.start_date, start_date)
        last = min(b.end_date, end_date + timedelta(days=1))
        if cur >= last:
            continue

        if group_by == "building":
            p = props.get(b.property_id)
            group_val = p.building_name if p else "N/A"
        elif group_by == "channel":
            group_val = chans.get(b.channel_id).channel_name if b.channel_id in chans else "N/A"
        elif group_by == "salesperson":
            sale = sales_map.get(b.salesperson_id)
            group_val = sale.name if sale else "Không có"
        else:
            p = props.get(b.property_id)
            group_val = (p.property_short or p.property_name) if p else "N/A"

        nightly_revenue = (b.total_payout_vnd or 0) / max(b.num_nights, 1)
        sale = sales_map.get(b.salesperson_id)
        nightly_commission = nightly_revenue * (sale.commission_rate if sale else 0)
        chan_name = chans.get(b.channel_id).channel_name if b.channel_id in chans else "N/A"

        d = cur
        while d < last:
            mk = date(d.year, d.month, 1)
            key = (mk, group_val)

            results[key]["sold_nights"] += 1
            results[key]["revenue"] += nightly_revenue
            results[key]["commission"] += nightly_commission

            if b.property_id:
                results[key]["prop_ids"].add(b.property_id)
                monthly_props_any[mk].add(b.property_id)

            monthly_sold[mk] += 1
            monthly_rev[mk] += nightly_revenue
            channel_totals[chan_name] += nightly_revenue

            if chan_name.lower() == "offline":
                monthly_offline_rev[mk] += nightly_revenue
            elif "airbnb" in chan_name.lower():
                monthly_airbnb_rev[mk] += nightly_revenue

            d += timedelta(days=1)

            

    all_groups = set()
    if group_by == "building":
        all_groups = {p.building_name or "N/A" for p in props.values()}
    elif group_by == "channel":
        all_groups = {c.channel_name for c in chans.values()}
    elif group_by == "salesperson":
        all_groups = {s.name for s in sales_map.values()}
    else:
        all_groups = {(p.property_short or p.property_name or "N/A") for p in props.values()}

    months_in_range = set(date(d.year, d.month, 1) for d in pd.date_range(start_date, end_date))
    for mk in months_in_range:
        for g in all_groups:
            key = (mk, g)
            if key not in results:
                results[key]

    rows = []
    totals_sold = totals_rev = totals_avail = total_comm = 0

    for (mk, group_val), agg in sorted(results.items()):
        sold = agg["sold_nights"]
        rev = int(round(agg["revenue"]))
        comm = int(round(agg["commission"]))
        adr = int(round(rev / sold)) if sold else 0

        if group_by == "building":
            active_props = len([p for p in props.values() if p.building_name == group_val])
        elif group_by == "channel":
            active_props = len([b for b in bookings if chans.get(b.channel_id) and chans[b.channel_id].channel_name == group_val])
        elif group_by == "salesperson":
            active_props = len([b for b in bookings if sales_map.get(b.salesperson_id) and sales_map[b.salesperson_id].name == group_val])
        else:
            active_props = 1

        avail = active_props * days_in_month(mk)
        vacant = avail - sold
        occ = round((sold / avail) * 100, 1) if avail else 0.0
        revpar = int(round(rev / avail)) if avail else 0

        totals_sold += sold
        totals_rev += rev
        totals_avail += avail
        total_comm += comm

        rows.append({
            "month": mk, "group": group_val, "sold_nights": sold,
            "vacant_nights": vacant, "revenue_vnd": rev, "adr_vnd": adr,
            "available_nights": avail, "occupancy_pct": occ,
            "revpar_vnd": revpar, "commission_vnd": comm
        })

    occupancy_gap = round(1 - (totals_sold / totals_avail), 4) if totals_avail else 0
    forecast_revenue = int(round(totals_rev * (1 + occupancy_gap - 0.1))) if totals_avail else totals_rev

    totals = {
        "vacant_nights": totals_avail - totals_sold,
        "sold_nights": totals_sold,
        "revenue_vnd": totals_rev,
        "available_nights": totals_avail,
        "commission_vnd": total_comm,
        "adr_vnd": int(round(totals_rev / totals_sold)) if totals_sold else 0,
        "occupancy_pct": round((totals_sold / totals_avail) * 100, 1) if totals_avail else 0.0,
        "revpar_vnd": int(round(totals_rev / totals_avail)) if totals_avail else 0,
        "forecast_revenue_vnd": forecast_revenue
    }

    months_sorted = sorted(monthly_sold.keys())
    chart = {
        "month_labels": [mk.strftime("%m/%Y") for mk in months_sorted],
        "sold_nights_by_month": [monthly_sold[mk] for mk in months_sorted],
        "revenue_by_month": [int(round(monthly_rev[mk])) for mk in months_sorted],
        "occupancy_pct_by_month": [],
        "airbnb_revenue_by_month": [int(round(monthly_airbnb_rev[mk])) for mk in months_sorted],
        "offline_revenue_by_month": [int(round(monthly_offline_rev[mk])) for mk in months_sorted]
        

    }
    for mk in months_sorted:
        avail = len(monthly_props_any[mk]) * days_in_month(mk)
        occ = round((monthly_sold[mk] / avail) * 100, 1) if avail else 0.0
        chart["occupancy_pct_by_month"].append(occ)

    if channel_totals:
        items = sorted(channel_totals.items(), key=lambda x: x[1], reverse=True)
        chart["channel_labels"] = [name or "Khác" for name, _ in items]
        chart["channel_revenue"] = [int(round(val)) for _, val in items]
    else:
        chart["channel_labels"] = []
        chart["channel_revenue"] = []

    return rows, totals, chart

@app.get("/reports/monthly", response_class=HTMLResponse)
async def report_monthly(
    request: Request,
    start: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end: Optional[str]   = Query(None, description="YYYY-MM-DD"),
    group_by: str = Query("property", description="property|building|channel|salesperson"),
    p: int = Query(1, ge=1),                      # <-- trang hiện tại
    page_size: int = Query(22, ge=5, le=200),     # <-- số dòng mỗi trang
):
    today = date.today()
    default_end = date(today.year, today.month, monthrange(today.year, today.month)[1])
    default_start = (default_end.replace(day=1) - timedelta(days=150)).replace(day=1)

    start_date = parse_date_mixed(start) or default_start
    end_date   = parse_date_mixed(end)   or default_end

    rows, totals, chart = compute_monthly_report(start_date, end_date, group_by)

    # ---------- PHÂN TRANG ----------
    total_rows = len(rows)
    pages = max(1, math.ceil(total_rows / page_size))
    page = min(max(1, p), pages)

    start_idx = (page - 1) * page_size
    end_idx   = min(start_idx + page_size, total_rows)
    rows_page = rows[start_idx:end_idx]

    pagination = {
        "page": page,
        "page_size": page_size,
        "total": total_rows,
        "pages": pages,
        "start": (start_idx + 1) if total_rows else 0,
        "end": end_idx,
    }

    # ---------- LOGIC BẢN ĐỒ (giữ nguyên của bạn) ----------
    geo_data = []
    if group_by in ['property', 'building']:
        with get_session() as session:
            query = (
                select(
                    Property.id,
                    Property.property_short,
                    Property.property_name,
                    Property.latitude,
                    Property.longitude,
                    Building.building_name,
                    Building.latitude.label("building_latitude"),
                    Building.longitude.label("building_longitude"),
                    func.sum(
                        case(
                            (Booking.num_nights > 0, func.coalesce(Booking.total_payout_vnd, 0) / Booking.num_nights),
                            else_=0
                        )
                    ).label("total_revenue"),
                    func.sum(
                        case(
                            (Booking.num_nights > 0, 1),
                            else_=0
                        )
                    ).label("nights_count")
                )
                .join(Property, Booking.property_id == Property.id)
                .join(Building, Property.building_id == Building.id, isouter=True)
                .where(Booking.start_date <= end_date, Booking.end_date > start_date)
                .where(or_(Booking.status.is_(None), not_(Booking.status.ilike("%hủy%"))))
                .group_by(Property.id, Building.id)
            )

            results = session.exec(query).all()
            
            if group_by == 'building':
                building_revenue = defaultdict(lambda: {'lat': None, 'lng': None, 'revenue': 0, 'nights': 0})
                for r in results:
                    if r.building_name:
                        key = r.building_name
                        building_revenue[key]['revenue'] += (r.total_revenue or 0)
                        building_revenue[key]['nights'] += r.nights_count
                        if not building_revenue[key]['lat'] and r.building_latitude:
                            building_revenue[key]['lat'] = r.building_latitude
                            building_revenue[key]['lng'] = r.building_longitude
                
                for name, data in building_revenue.items():
                    if data['lat'] and data['lng']:
                        geo_data.append({
                            "name": name,
                            "lat": data['lat'],
                            "lng": data['lng'],
                            "revenue": int(data['revenue']),
                            "sold_nights": data['nights'],
                            "occupancy_pct": 0
                        })
            else:
                for r in results:
                    lat = r.latitude if r.latitude else r.building_latitude
                    lng = r.longitude if r.longitude else r.building_longitude
                    if lat and lng:
                        geo_data.append({
                            "name": r.property_short or r.property_name,
                            "lat": lat,
                            "lng": lng,
                            "revenue": int(r.total_revenue or 0),
                            "sold_nights": r.nights_count,
                            "occupancy_pct": 0
                        })

    return templates.TemplateResponse("reports_monthly.html", {
        "request": request,
        "rows": rows_page,          # chỉ trả trang hiện tại
        "start": start_date,
        "end": end_date,
        "group_by": group_by,
        "totals": totals,
        "chart": chart,
        "geo_data": geo_data,
        "pagination": pagination,   # thông tin phân trang
    })


@app.get("/reports/monthly/export")
async def report_monthly_export(
    start: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end: Optional[str]   = Query(None, description="YYYY-MM-DD"),
    group_by: str = Query("property", description="property|building|channel"),
    fmt: str = Query("xlsx", description="xlsx|csv")
):
    import pandas as pd
    started = datetime.utcnow()

    today = date.today()
    default_end = date(today.year, today.month, monthrange(today.year, today.month)[1])
    default_start = (default_end.replace(day=1) - timedelta(days=150)).replace(day=1)

    start_date = parse_date_mixed(start) or default_start
    end_date = parse_date_mixed(end) or default_end

    rows, totals, chart = compute_monthly_report(start_date, end_date, group_by)

    # Chuẩn bị DataFrame
    df = pd.DataFrame([{
        "Tháng": r["month"].strftime("%m/%Y"),
        "Nhóm": r["group"],
        "Đêm bán": r["sold_nights"],
        "Đêm khả dụng": r["available_nights"],
        "Tỷ lệ lấp đầy (%)": r["occupancy_pct"],
        "Doanh thu (VND)": r["revenue_vnd"],
        "ADR (VND)": r["adr_vnd"],
        "RevPAR (VND)": r["revpar_vnd"],
    } for r in rows])

    buf = BytesIO()
    filename = f"monthly_report_{group_by}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{fmt}"

    if fmt.lower() == "csv":
        df.to_csv(buf, index=False, encoding="utf-8-sig")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        # Excel
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

@app.get("/debug/channels")
def debug_channels():
    with get_session() as session:
        channels = session.exec(select(Channel)).all()
        return [{"id": c.id, "name": c.channel_name} for c in channels]

@app.get("/debug/bookings-offline")
def debug_bookings_offline():
    with get_session() as session:
        offline = session.exec(select(Channel).where(Channel.channel_name == "Offline")).first()
        if not offline:
            return {"offline_id": None, "count": 0, "bookings": []}

        bookings = session.exec(select(Booking).where(Booking.channel_id == offline.id)).all()
        results = [
            {
                "id": b.id,
                "confirmation_code": b.confirmation_code,
                "start_date": str(b.start_date),
                "end_date": str(b.end_date),
                "payout": b.total_payout_vnd,
            }
            for b in bookings
        ]
        return {
            "offline_id": offline.id,
            "count": len(results),
            "bookings": results,
        }

def build_airbnb_url(page: int, limit: int = 40) -> str:
    offset = (page - 1) * limit
    base = "https://www.airbnb.com.vn/api/v2/download_reservations"
    params = {
        "_format": "for_remy",
        "_limit": str(limit),
        "_offset": str(offset),
        "collection_strategy": "for_reservations_list",
        "sort_field": "start_date",
        "sort_order": "desc",
        "status": "accepted,request,canceled",  # giữ dấu phẩy
        "page": str(page),
        "key": "d306zoyjsyarp7ifhu67rjxn52tv0t20",
        "currency": "VND",
        "locale": "vi",
    }
    return f"{base}?{urlencode(params, safe=',')}"

@app.get("/airbnb/csv-batch")
async def airbnb_csv_batch(page_from: int = 1, page_to: int = 1, limit: int = 40):
    cookie = os.getenv("AIRBNB_COOKIE", "").strip()
    if not cookie:
        return HTMLResponse("Thiếu AIRBNB_COOKIE trong .env (copy giá trị Cookie từ request download_reservations).", status_code=400)

    buf = io.BytesIO()
    async with httpx.AsyncClient(timeout=60.0, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv,*/*;q=0.8",
        "Cookie": cookie,
    }) as client, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in range(page_from, page_to + 1):
            url = build_airbnb_url(p, limit)
            r = await client.get(url)
            if r.status_code == 200:
                zf.writestr(f"reservations_page_{p}.csv", r.content)
            else:
                # ghi file báo lỗi để biết trang nào fail
                zf.writestr(f"page_{p}_ERROR.txt", f"HTTP {r.status_code} at {url}")

    buf.seek(0)
    filename = f"airbnb_pages_{page_from}-{page_to}.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/airbnb/ingest", response_class=HTMLResponse)
async def airbnb_ingest(
    request: Request,
    page_from: int = Query(1, ge=1),
    page_to:   int = Query(1, ge=1),
    limit:     int = Query(40, ge=1, le=200),
    delay_ms:  int = Query(800, ge=0),
):
    cookie = os.getenv("AIRBNB_COOKIE", "").strip()
    if not cookie:
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "msg": "Chưa thiết lập AIRBNB_COOKIE trong .env (copy giá trị Cookie từ DevTools).",
            "success": False
        })

    summaries = []
    total_inserted = total_updated = 0

    try:
        async with httpx.AsyncClient(timeout=60.0, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/csv,*/*;q=0.8",
            "Cookie": cookie,
        }) as client:

            with get_session() as session:
                airbnb = session.exec(select(Channel).where(Channel.channel_name == "Airbnb")).first()

                for p in range(page_from, page_to + 1):
                    url = build_airbnb_url(p, limit)
                    r = await client.get(url)
                    if r.status_code != 200:
                        summaries.append(f"Trang {p}: HTTP {r.status_code}")
                        await asyncio.sleep(delay_ms/1000)
                        continue

                    df = pd.read_csv(pd.io.common.BytesIO(r.content))
                    rows_inserted = rows_updated = 0

                    for _, row in df.iterrows():
                        cc_col = pick(df, "confirmation_code")
                        if not cc_col: continue
                        cc = str(row.get(cc_col, "")).strip()
                        if not cc: continue

                        status_col = pick(df, "status")
                        status = str(row.get(status_col, "")).strip() if status_col else None
                        gname_col = pick(df, "guest_name")
                        guest_name = str(row.get(gname_col, "")).strip() if gname_col else None
                        gcontact_col = pick(df, "guest_contact")
                        guest_contact = str(row.get(gcontact_col, "")).strip() if gcontact_col else None

                        st_col = pick(df, "start_date")
                        en_col = pick(df, "end_date")
                        bk_col = pick(df, "booking_date")
                        start_date = parse_date_mixed(row.get(st_col)) if st_col else None
                        end_date   = parse_date_mixed(row.get(en_col)) if en_col else None
                        booking_date = parse_date_mixed(row.get(bk_col)) if bk_col else None

                        nights_col = pick(df, "num_nights")
                        num_nights = row.get(nights_col) if nights_col else None
                        try:
                            num_nights = int(num_nights) if pd.notna(num_nights) else None
                        except Exception:
                            num_nights = None
                        if start_date and end_date:
                            dcalc = (end_date - start_date).days
                            if dcalc > 0: num_nights = dcalc

                        ad_col = pick(df, "num_adults")
                        ch_col = pick(df, "num_children")
                        inf_col = pick(df, "num_infants")
                        num_adults  = int(row.get(ad_col))  if ad_col and pd.notna(row.get(ad_col)) else None
                        num_children= int(row.get(ch_col))  if ch_col and pd.notna(row.get(ch_col)) else None
                        num_infants = int(row.get(inf_col)) if inf_col and pd.notna(row.get(inf_col)) else None

                        lst_col = pick(df, "listing")
                        listing = str(row.get(lst_col, "")).strip() if lst_col else None
                        inc_col = pick(df, "income")
                        income_vnd = parse_vnd(row.get(inc_col)) if inc_col else None

                        # mapping building/property
                        bld_name, unit_num = parse_building_and_unit(listing)
                        bld_code = building_code_from_name(bld_name) if bld_name else None
                        unit_short = unit_short_from_unit_number_auto(unit_num) if unit_num else None
                        prop_short = f"{bld_code}-{unit_short}" if (bld_code and unit_short) else None

                        building = None
                        if bld_name:
                            building = session.exec(select(Building).where(Building.building_name == bld_name)).first()
                            if not building:
                                building = Building(building_name=bld_name, building_code=bld_code)
                                session.add(building); session.commit(); session.refresh(building)

                        prop = None
                        if listing:
                            prop = session.exec(select(Property).where(Property.property_name == listing)).first()
                            if not prop:
                                prop = Property(
                                    property_name=listing,
                                    building_id=building.id if building else None,
                                    building_name=bld_name, building_code=bld_code,
                                    unit_number=unit_num, unit_short=unit_short, property_short=prop_short
                                )
                                session.add(prop); session.commit(); session.refresh(prop)
                            else:
                                updated=False
                                if (not prop.building_id) and building: prop.building_id=building.id; updated=True
                                if (not prop.building_name) and bld_name: prop.building_name=bld_name; updated=True
                                if (not prop.building_code) and bld_code: prop.building_code=bld_code; updated=True
                                if (not prop.unit_number) and unit_num: prop.unit_number=unit_num; updated=True
                                if (not prop.unit_short) and unit_short: prop.unit_short=unit_short; updated=True
                                if (not prop.property_short) and prop_short: prop.property_short=prop_short; updated=True
                                if updated: session.add(prop); session.commit()

                        existing = session.exec(select(Booking).where(Booking.confirmation_code == cc)).first()
                        if existing:
                            existing.property_id = prop.id if prop else existing.property_id
                            existing.channel_id  = airbnb.id if airbnb else existing.channel_id
                            existing.start_date  = start_date or existing.start_date
                            existing.end_date    = end_date or existing.end_date
                            if num_nights  is not None: existing.num_nights  = num_nights
                            if num_adults  is not None: existing.num_adults  = num_adults
                            if num_children is not None: existing.num_children= num_children
                            if num_infants is not None: existing.num_infants = num_infants
                            existing.booking_date = booking_date or existing.booking_date
                            existing.status       = status or existing.status
                            if income_vnd is not None: existing.total_payout_vnd = income_vnd
                            existing.guest_name   = guest_name or existing.guest_name
                            existing.guest_contact= guest_contact or existing.guest_contact
                            existing.listing_raw  = listing or existing.listing_raw
                            session.add(existing)
                            rows_updated += 1
                        else:
                            b = Booking(
                                confirmation_code=cc,
                                property_id=prop.id if prop else None,
                                channel_id=airbnb.id if airbnb else None,
                                start_date=start_date, end_date=end_date,
                                num_nights=num_nights,
                                num_adults=num_adults, num_children=num_children, num_infants=num_infants,
                                booking_date=booking_date, status=status,
                                total_payout_vnd=income_vnd,
                                guest_name=guest_name, guest_contact=guest_contact,
                                listing_raw=listing,
                            )
                            session.add(b)
                            rows_inserted += 1

                    session.commit()
                    summaries.append(f"Trang {p}: +{rows_inserted} mới, {rows_updated} cập nhật")
                    total_inserted += rows_inserted
                    total_updated  += rows_updated
                    await asyncio.sleep(delay_ms/1000)

    except Exception as e:
        return templates.TemplateResponse("upload.html", {
            "request": request, "msg": f"Lỗi ingest: {e}", "success": False
        })

    # log tổng cho lần ingest này
    with get_session() as session:
        session.add(ImportLog(
            filename=f"airbnb:pages:{page_from}-{page_to}",
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            status="success",
            rows_inserted=total_inserted,
            rows_updated=total_updated,
            message="; ".join(summaries)[:1000]
        ))
        session.commit()

    # hiển thị kết quả trên UI
    last_ingest = None
    with get_session() as session:
        last_ingest = session.exec(
            select(ImportLog)
            .where(ImportLog.filename.ilike("airbnb:%"))
            .order_by(ImportLog.finished_at.desc())
        ).first()
    next_run = get_next_run_time() if 'get_next_run_time' in globals() else None

    msg = f"Đã xử lý {page_from}→{page_to} (limit {limit}). Tổng: +{total_inserted} mới, {total_updated} cập nhật. " + " · ".join(summaries)
    return templates.TemplateResponse("upload.html", {
        "request": request, "msg": msg, "success": True,
        "ingest_last": last_ingest, "ingest_next": next_run
    })
    
@app.get("/buildings", response_class=HTMLResponse)
async def show_buildings(request: Request):
    with get_session() as session:
        buildings = session.exec(select(Building)).all()

        # Tính số căn mỗi tòa
        building_data = []
        for b in buildings:
            num_props = session.exec(
                select(func.count()).where(Property.building_id == b.id)
            ).one()
            building_data.append({
                "id": b.id,
                "building_name": b.building_name,
                "building_code": b.building_code,
                "address": b.address,
                "num_properties": num_props
            })


    return templates.TemplateResponse("buildings.html", {
    "request": request,
    "buildings": building_data
    })

@app.post("/buildings/new")
async def add_building(
    building_name: str = Form(...),
    building_code: str = Form(None),
    address: str = Form(None)
):
    with get_session() as session:
        b = Building(building_name=building_name, building_code=building_code, address=address)
        session.add(b)
        session.commit()
    return RedirectResponse(url="/buildings", status_code=303)    

@app.get("/properties", response_class=HTMLResponse)
async def show_properties(request: Request):
    with get_session() as session:
        properties = session.exec(select(Property)).all()
        buildings = session.exec(select(Building)).all()

        # Map building_id to building_name
        building_map = {b.id: b.building_name for b in buildings}
        for p in properties:
            p.building_name = building_map.get(p.building_id, "-")

    return templates.TemplateResponse("properties.html", {
        "request": request,
        "properties": properties,
        "buildings": buildings
    })

@app.post("/properties/new")
async def add_property(
    property_name: str = Form(...),
    airbnb_name: str = Form(None),
    building_id: int = Form(...)
):
    with get_session() as session:
        prop = Property(
            property_name=property_name,
            airbnb_name=airbnb_name,
            building_id=building_id
        )
        session.add(prop)
        session.commit()
    return RedirectResponse(url="/properties", status_code=303)

@app.get("/properties/edit/{property_id}", response_class=HTMLResponse)
def edit_property_form(request: Request, property_id: int):
    with get_session() as session:
        prop = session.get(Property, property_id)
        buildings = session.exec(select(Building)).all()
        return templates.TemplateResponse("edit_property.html", {
            "request": request,
            "property": prop,
            "buildings": buildings
        })


@app.post("/properties/edit/{property_id}")
def update_property(property_id: int,
                    property_name: str = Form(...),
                    airbnb_name: str = Form(None),
                    building_id: int = Form(...)):
    with get_session() as session:
        prop = session.get(Property, property_id)
        if prop:
            prop.property_name = property_name
            prop.airbnb_name = airbnb_name
            prop.building_id = building_id
            session.add(prop)
            session.commit()
    return RedirectResponse("/properties", status_code=303)


@app.post("/properties/delete/{property_id}")
def delete_property(property_id: int):
    with get_session() as session:
        prop = session.get(Property, property_id)
        if prop:
            session.delete(prop)
            session.commit()
    return RedirectResponse("/properties", status_code=303)

