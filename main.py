from fastapi import FastAPI, Request, UploadFile, File, Query, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from sqlmodel import select, Session, func
from sqlalchemy import or_, not_, case, func

import pandas as pd
import uuid
import os
import io
import zipfile
import asyncio
import math
import httpx

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Service Layer Imports
from services.booking_service import BookingService
from services.property_service import PropertyService
from services.revenue_service import RevenueService
from services.upload_service import UploadService
from services.salesperson_service import SalespersonService
from services.initialization_service import InitializationService
from datetime import datetime, date, timedelta
from calendar import monthrange
from collections import defaultdict
from types import SimpleNamespace
from typing import Optional, List
from urllib.parse import urlencode

from dotenv import load_dotenv
load_dotenv()  # <-- để tự động nạp .env

from db import init_db, get_session, get_session_context
from models import Booking, Property, Channel, ImportLog, Building, Salesperson, ExtraCharge, ExpenseCategory, User
from utils import parse_date_mixed

# routers OPEX
from routes_expense import (
    router as expense_router,
    rec_router as recurring_router,
    aux as expense_aux_router,
    extra_charges_router,
)

# Authentication
from auth.routes import router as auth_router
from auth.dependencies import get_optional_current_user, get_current_active_user
from routes_extra_fees import extra_fees_router
from routes_brain import router as brain_router



# --- Mật khẩu quản trị ---
PASSWORD = os.getenv("ADMIN_PASSWORD", "ocean2025")

# --- Middleware bảo vệ truy cập ---
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (request.url.path.startswith("/login") or 
            request.url.path.startswith("/static") or
            request.url.path.startswith("/brain") or
            request.url.path.startswith("/.brain/")):  # Allow brain system access
            return await call_next(request)

        session_token = request.cookies.get("session")
        if session_token != PASSWORD:
            return RedirectResponse(url="/login")

        return await call_next(request)

# Global scheduler variable
scheduler = None

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with proper scheduler initialization."""
    global scheduler
    
    # Startup
    print("[Startup] Initializing application...")
    init_db()
    with get_session_context() as session:
        # Use service to ensure default channels
        init_service = InitializationService(session, None)
        init_service.ensure_default_channels()

    # Initialize scheduler with proper async handling
    if os.getenv("AIRBNB_COOKIE", "").strip():
        try:
            scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")
            scheduler.add_job(
                _trigger_ingest_page1,
                CronTrigger(hour=2, minute=0),
                id="daily_ingest",
                name="Daily Airbnb Data Ingest"
            )
            scheduler.start()
            print("[Scheduler] Daily ingest scheduled at 02:00 Asia/Ho_Chi_Minh")
        except Exception as e:
            print(f"[Scheduler] Failed to initialize: {e}")
            scheduler = None
    else:
        print("[Scheduler] Skip: AIRBNB_COOKIE not set")

    print("[Startup] Application startup complete")
    
    yield  # Application runs here
    
    # Shutdown
    print("[Shutdown] Shutting down application...")
    if scheduler:
        try:
            scheduler.shutdown()
            print("[Scheduler] Stopped successfully")
        except Exception as e:
            print(f"[Scheduler] Shutdown error: {e}")
    print("[Shutdown] Application shutdown complete")

# ✅ Khởi tạo FastAPI với lifespan
app = FastAPI(
    title="Airbnb Revenue Management System",
    lifespan=lifespan
)
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth_router)  # Authentication routes
app.include_router(expense_router)
app.include_router(recurring_router)
app.include_router(expense_aux_router)
app.include_router(extra_charges_router)
app.include_router(extra_fees_router)
app.include_router(brain_router)  # Brain management dashboard - Internal developer tool

# Mount .brain folder as static files for brain system access
app.mount("/.brain", StaticFiles(directory=".brain"), name="brain_files")

# Route hiển thị giao diện phụ phí căn hộ
@app.get("/property_charges", response_class=HTMLResponse)
def property_charges_page(request: Request):
    return templates.TemplateResponse("property_charges.html", {"request": request})

@app.get("/expenses/ledger", response_class=HTMLResponse)
def expenses_ledger(request: Request):
    return templates.TemplateResponse("expenses_ledger.html", {"request": request, "month": ""})


# --- Jinja2 Filters ---
def vn_date(v):
    if not v: return ""
    try: return v.strftime("%d/%m/%Y")
    except: return str(v)

def vn_month(v):
    if not v: return ""
    try: return v.strftime("%m/%Y")
    except: return str(v)

def vnd(v):
    try: return f"{int(v):,}"
    except: return "0"

def vn_dt(v):
    if not v: return ""
    try: return v.strftime("%d/%m/%Y %H:%M")
    except: return str(v)

templates.env.filters["vn_date"] = vn_date
templates.env.filters["vn_month"] = vn_month
templates.env.filters["vnd"] = vnd
templates.env.filters["vn_dt"] = vn_dt


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_submit(response: Response, password: str = Form(...)):
    if password == PASSWORD:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("session", PASSWORD, httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": {}, "error": "Sai mật khẩu"})

def _get_total_properties():
    try:
        with get_session_context() as session:
            init_service = InitializationService(session, None)
            result = init_service.get_total_properties()
            return result.get("data", {}).get("total_properties", 0)
    except Exception as e:
        print("WARNING: Cannot compute total properties dynamically:", e)
        return 0

def get_next_run_time():
    try:
        if scheduler:
            jobs = scheduler.get_jobs()
            if jobs:
                return jobs[0].next_run_time
    except Exception:
        pass
    return None



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


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, msg: Optional[str] = None, success: Optional[bool] = None):
    last_ingest = None
    with get_session_context() as session:
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


@app.get("/test-upload")
async def test_upload():
    """Test route để debug upload issue."""
    return {"message": "Upload route accessible"}

@app.get("/upload", response_class=HTMLResponse)
async def show_upload_form(request: Request):
    """Hiển thị form upload CSV."""
    try:
        return templates.TemplateResponse("upload_simple.html", {"request": request})
    except Exception as e:
        return HTMLResponse(f"Template error: {str(e)}", status_code=500)

@app.post("/upload", response_class=HTMLResponse)
async def upload(
    request: Request, 
    files: List[UploadFile] = File(...),
    room_mapping: Optional[str] = Form(None),
    user: Optional[User] = Depends(get_optional_current_user)
):
    """Upload CSV với room mapping support."""
    with get_session_context() as session:
        upload_service = UploadService(session, user)
        
        # Parse room mapping data if provided
        room_mapping_data = None
        if room_mapping:
            try:
                import json
                room_mapping_data = json.loads(room_mapping)
            except json.JSONDecodeError:
                return templates.TemplateResponse("upload.html", {
                    "request": request,
                    "msg": "Dữ liệu Room Mapping không hợp lệ",
                    "success": False
                })
        
        # Use service for processing
        result = upload_service.process_upload_files(files, room_mapping_data)
        
        if result["success"]:
            # Tạo message chi tiết bằng tiếng Việt
            totals = result.get("data", {}).get("totals", {})
            inserted = totals.get("inserted", 0)
            updated = totals.get("updated", 0)
            processing_time = totals.get("processing_time", 0)
            
            # Tạo thống kê chi tiết
            stats_msg = f"✅ Tải lên thành công!"
            if inserted > 0 or updated > 0:
                stats_msg += f"\n📊 Thống kê: {inserted} bản ghi mới, {updated} bản ghi cập nhật"
            if processing_time > 0:
                stats_msg += f"\n⏱️ Thời gian xử lý: {processing_time:.2f} giây"
            
            # Hiển thị chi tiết từng file nếu có
            summaries = result.get("data", {}).get("summaries", [])
            if len(summaries) > 1:
                stats_msg += f"\n📁 Đã xử lý {len(summaries)} file"
            
            return templates.TemplateResponse("upload.html", {
                "request": request,
                "msg": stats_msg,
                "success": True,
                "upload_stats": totals  # Truyền thêm stats để template có thể dùng
            })
        else:
            return templates.TemplateResponse("upload.html", {
                "request": request,
                "msg": f"❌ Lỗi upload: {result.get('error', 'Unknown error')}",
                "success": False
            })


# 1. HIỂN THỊ FORM THÊM MỚI (ĐẶT LÊN ĐẦU TIÊN)

@app.get("/bookings/new", response_class=HTMLResponse)
async def show_add_booking_form(
    request: Request,
    channel: Optional[str] = Query(None),      # ví dụ: ?channel=Offline
    channel_id: Optional[int] = Query(None),   # ví dụ: ?channel_id=2
    offline: Optional[bool] = Query(False)     # ví dụ: ?offline=1
):
    """Hiển thị form để thêm booking mới, hỗ trợ chọn sẵn kênh."""
    with get_session_context() as session:
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
    with get_session_context() as session:
        user = get_optional_current_user(request)
        booking_service = BookingService(session, user)
        
        if not confirmation_code:
            confirmation_code = f"OFF-{uuid.uuid4().hex[:8].upper()}"

        num_nights = (end_date - start_date).days

        # Prepare booking data
        booking_data = {
            "property_id": property_id,
            "channel_id": channel_id,
            "confirmation_code": confirmation_code,
            "start_date": start_date,
            "end_date": end_date,
            "num_nights": num_nights,
            "total_payout_vnd": total_payout_vnd,
            "guest_name": guest_name,
            "guest_contact": guest_contact,
            "status": "xác nhận",
            "booking_date": date.today(),
            "salesperson_id": salesperson_id,
            "notes": notes
        }
        
        # Use service to create booking
        result = booking_service.create_booking(booking_data)
        if not result["success"]:
            # Handle error case if needed
            pass

    return RedirectResponse(url="/bookings", status_code=303)
 

@app.get("/bookings/{booking_id}/edit", response_class=HTMLResponse)
async def edit_booking_form(request: Request, booking_id: int):
    with get_session_context() as session:
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
    with get_session_context() as session:
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
    with get_session_context() as session:
        booking = session.get(Booking, booking_id)
        if booking:
            session.delete(booking)
            session.commit()
    return RedirectResponse("/bookings", status_code=303)

# ============ ROOM ASSIGNMENT ROUTES ============

@app.get("/bookings/{booking_id}/room-assignment", response_class=HTMLResponse)
async def get_room_assignment_form(request: Request, booking_id: int):
    """Display room assignment form for a booking."""
    with get_session_context() as session:
        booking_service = BookingService(session)
        
        # Get booking
        booking_result = booking_service.get_booking_detail(booking_id)
        if not booking_result["success"]:
            return templates.TemplateResponse("upload.html", {
                "request": request,
                "msg": booking_result["message"],
                "success": False
            })
        
        booking = booking_result["data"]
        
        # Get existing room assignment
        assignment_result = booking_service.get_booking_room_assignment(booking_id)
        room_assignment = assignment_result["data"] if assignment_result["success"] else None
        
        # Get properties for dropdown
        properties = session.exec(select(Property).order_by(Property.property_short, Property.property_name)).all()
        
        return templates.TemplateResponse("room_assignment.html", {
            "request": request,
            "booking": booking,
            "room_assignment": room_assignment,
            "properties": properties
        })

@app.post("/bookings/{booking_id}/room-assignment")
async def handle_room_assignment(
    booking_id: int,
    booked_room: str = Form(...),
    actual_room: str = Form(...),
    revenue_attribution: str = Form(...),
    change_reason: str = Form(...),
    changed_date: Optional[date] = Form(None),
    changed_by: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """Handle room assignment creation/update."""
    with get_session_context() as session:
        booking_service = BookingService(session)
        
        assignment_data = {
            "booked_room": booked_room.strip() if booked_room else None,
            "actual_room": actual_room.strip() if actual_room else None,
            "revenue_attribution": revenue_attribution,
            "change_reason": change_reason if change_reason else None,
            "changed_date": changed_date,
            "changed_by": changed_by.strip() if changed_by else None,
            "notes": notes.strip() if notes else None
        }
        
        result = booking_service.create_room_assignment(booking_id, assignment_data)
        
        if result["success"]:
            return RedirectResponse(f"/bookings/{booking_id}", status_code=303)
        else:
            # Return to form with error
            booking_result = booking_service.get_booking_detail(booking_id)
            return templates.TemplateResponse("room_assignment.html", {
                "request": {},
                "booking": booking_result["data"] if booking_result["success"] else None,
                "room_assignment": None,
                "error": result["message"]
            })

# ============ /ROOM ASSIGNMENT ROUTES ============

@app.get("/salespeople", response_class=HTMLResponse)
async def manage_salespeople(request: Request):
    """Hiển thị trang quản lý nhân viên sale."""
    with get_session_context() as session:
        salesperson_service = SalespersonService(session)
        salespeople = salesperson_service.get_all_salespeople()
        return templates.TemplateResponse("salespeople.html", {
            "request": request,
            "salespeople": salespeople
        })

@app.post("/salespeople/new")
async def handle_add_salesperson(
    name: str = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None), 
    commission_rate_pct: float = Form(...)
):
    """Xử lý thêm nhân viên sale mới."""
    with get_session_context() as session:
        salesperson_service = SalespersonService(session)
        result = salesperson_service.create_salesperson(name, commission_rate_pct, email, phone)
        
    return RedirectResponse(url="/salespeople", status_code=303)

# 2. HIỂN THỊ CHI TIẾT 1 BOOKING (ĐẶT SAU /new)
@app.get("/bookings/{booking_id}", response_class=HTMLResponse)
async def get_booking_detail(request: Request, booking_id: int):
    """
    Handles displaying the detailed view for a single booking with room assignment info.
    """
    with get_session_context() as session:
        booking_service = BookingService(session)
        
        # Get booking detail
        booking_result = booking_service.get_booking_detail(booking_id)
        if not booking_result["success"]:
            return templates.TemplateResponse("upload.html", {
                "request": request,
                "msg": booking_result["message"],
                "success": False
            })
        
        booking = booking_result["data"]
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

        # Get room assignment info
        room_assignment_result = booking_service.get_booking_room_assignment(booking_id)
        room_assignment = room_assignment_result["data"] if room_assignment_result["success"] else None
        
        # Get revenue attribution
        revenue_result = booking_service.calculate_room_revenue_attribution(booking_id)
        revenue_attribution = revenue_result["data"] if revenue_result["success"] else None

        return templates.TemplateResponse("booking_detail.html", {
            "request": request,
            "b": booking_vm,
            "room_assignment": room_assignment,
            "revenue_attribution": revenue_attribution
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
    property_name: Optional[str] = Query(None),  # Đã thêm dấu ngoặc đóng
    p: int = Query(1, ge=1),                    # <-- trang hiện tại
    page_size: int = Query(50, ge=10, le=200),  # <-- số dòng / trang
):
    start_date = parse_date_mixed(start) if start else None
    end_date   = parse_date_mixed(end)   if end else None

    with get_session_context() as session:
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
    with get_session_context() as session:
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

        # Tích hợp phụ phí theo charge_name
        extra_charges = session.exec(
            select(ExtraCharge.charge_month, ExtraCharge.charge_name, func.sum(ExtraCharge.charge_amount))
            .where(ExtraCharge.charge_month >= start_date.strftime("%Y-%m"), ExtraCharge.charge_month <= end_date.strftime("%Y-%m"))
            .group_by(ExtraCharge.charge_month, ExtraCharge.charge_name)
        ).all()
        extra_charges_map = defaultdict(lambda: defaultdict(float))
        for ec in extra_charges:
            charge_month = date(int(ec[0][:4]), int(ec[0][5:]), 1)  # Chuyển "YYYY-MM" thành date
            extra_charges_map[charge_month][ec[1]] += ec[2]

        # Fix: Thêm category_map để tránh lỗi
        categories = session.exec(select(ExpenseCategory)).all()
        category_map = {cat.id: cat.name for cat in categories}

    results = defaultdict(lambda: {"sold_nights": 0, "revenue": 0.0, "commission": 0.0, "prop_ids": set(), "expenses": defaultdict(float)})
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

    # Tích hợp phụ phí vào doanh thu và chi phí hàng tháng
    for mk in monthly_rev.keys():
        if mk in extra_charges_map:
            for cat_id, amount in extra_charges_map[mk].items():
                monthly_rev[mk] += amount
                for key in results.keys():
                    if key[0] == mk:
                        results[key]["expenses"][cat_id] += amount

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

        # Fix: Sử dụng charge_name thay vì category_id
        # expense_details = {category_map[cat_id]: int(round(amount)) for cat_id, amount in agg["expenses"].items()}

        rows.append({
            "month": mk, "group": group_val, "sold_nights": sold,
            "vacant_nights": vacant, "revenue_vnd": rev, "adr_vnd": adr,
            "available_nights": avail, "occupancy_pct": occ,
            "revpar_vnd": revpar, "commission_vnd": comm
        })

    # --- tổng hợp KPI cho tiêu đề báo cáo ---
    total_rows = len(rows)
    total_revenue = int(round(sum(r["revenue_vnd"] for r in rows)))
    total_commission = int(round(sum(r["commission_vnd"] for r in rows)))
    total_sold_nights = sum(r["sold_nights"] for r in rows)
    total_vacant_nights = sum(r["vacant_nights"] for r in rows)
    total_available_nights = sum(r["available_nights"] for r in rows)

    total_occupancy_pct = round((total_sold_nights / total_available_nights) * 100, 1) if total_available_nights else 0.0
    total_revpar_vnd = int(round(total_revenue / total_available_nights)) if total_available_nights else 0

    # --- trend data cho chart ---
    monthly_trend = defaultdict(lambda: {"sold_nights": 0, "revenue": 0.0, "commission": 0.0})
    for (mk, group_val), agg in results.items():
        sold = agg["sold_nights"]
        rev = agg["revenue"]
        comm = agg["commission"]

        monthly_trend[mk]["sold_nights"] += sold
        monthly_trend[mk]["revenue"] += rev
        monthly_trend[mk]["commission"] += comm

    # sắp xếp theo tháng
    sorted_trend = sorted(monthly_trend.items())

    # tách riêng tháng và dữ liệu
    trend_months = [m[0].strftime("%Y-%m") if hasattr(m[0], 'strftime') else str(m[0]) for m in sorted_trend]  # Fix: Convert dates to strings
    trend_data = [m[1] for m in sorted_trend]

    # --- pie chart data cho doanh thu theo kênh ---
    channel_revenue_pie = defaultdict(float)
    for chan_name, rev in channel_totals.items():
        channel_revenue_pie[chan_name] += rev

    sorted_channel_revenue = sorted(channel_revenue_pie.items(), key=lambda x: x[1], reverse=True)

    # tính tổng doanh thu để tính tỷ lệ phần trăm
    total_channel_revenue = sum(channel_revenue_pie.values())

    # thêm thông tin phần trăm vào dữ liệu pie chart
    channel_revenue_pie_data = [
        {"channel": chan, "revenue": int(round(rev)), "percentage": round((rev / total_channel_revenue) * 100, 2) if total_channel_revenue > 0 else 0}
        for chan, rev in sorted_channel_revenue
    ]

    # Prepare chart data in format expected by template JavaScript
    month_labels = trend_months
    revenue_by_month = [d["revenue"] for d in trend_data]
    sold_nights_by_month = [d["sold_nights"] for d in trend_data]
    occupancy_pct_by_month = []
    airbnb_revenue_by_month = []
    offline_revenue_by_month = []

    # Prepare pie chart data
    channel_labels = [item["channel"] for item in channel_revenue_pie_data]
    channel_revenue_values = [item["revenue"] for item in channel_revenue_pie_data]

    # Calculate monthly metrics for charts
    for mk in [datetime.strptime(m, "%Y-%m").date() for m in month_labels]:
        # For occupancy calculation, we need to aggregate differently
        month_revenue = monthly_rev.get(mk, 0)
        month_sold = monthly_sold.get(mk, 0)
        month_airbnb = monthly_airbnb_rev.get(mk, 0)
        month_offline = monthly_offline_rev.get(mk, 0)
        
        # Calculate available nights for this month  
        month_props = len(monthly_props_any.get(mk, set()))
        month_available = month_props * days_in_month(mk) if month_props > 0 else 0
        month_occ = round((month_sold / month_available) * 100, 1) if month_available > 0 else 0
        
        occupancy_pct_by_month.append(month_occ)
        airbnb_revenue_by_month.append(int(month_airbnb))
        offline_revenue_by_month.append(int(month_offline))

    # Prepare pie chart data in template format
    channel_labels = [item["channel"] for item in channel_revenue_pie_data]
    channel_revenue_values = [item["revenue"] for item in channel_revenue_pie_data]

    return {
        "group_by": group_by,
        "start_date": start_date,
        "end_date": end_date,
        "rows": rows,
        "total": {
            "sold_nights": total_sold_nights,
            "vacant_nights": total_vacant_nights,
            "revenue_vnd": total_revenue,
            "adr_vnd": total_revpar_vnd,
            "available_nights": total_available_nights,
            "occupancy_pct": total_occupancy_pct,
            "commission_vnd": total_commission,  # Fix: Sử dụng biến đúng
        },
        # Chart data in format expected by template
        "chart_data": {
            "month_labels": month_labels,
            "revenue_by_month": revenue_by_month,
            "sold_nights_by_month": sold_nights_by_month,
            "occupancy_pct_by_month": occupancy_pct_by_month,
            "airbnb_revenue_by_month": airbnb_revenue_by_month,
            "offline_revenue_by_month": offline_revenue_by_month,
            # Pie chart data for template
            "channel_labels": channel_labels,
            "channel_revenue": channel_revenue_values,
        },
        "channel_revenue_pie": channel_revenue_pie_data,
    }

# ================= ROUTE BÁO CÁO BỊ THIẾU =================

@app.get("/reports/monthly", response_class=HTMLResponse)
async def report_monthly(
    request: Request,
    start: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end: Optional[str]   = Query(None, description="YYYY-MM-DD"),
    group_by: str = Query("property", description="property|building|channel|salesperson"),
    p: int = Query(1, ge=1),                      # <-- trang hiện tại
    page_size: int = Query(22, ge=5, le=200),     # <-- số dòng mỗi trang
):
    try:
        today = date.today()
        default_end = date(today.year, today.month, monthrange(today.year, today.month)[1])
        default_start = (default_end.replace(day=1) - timedelta(days=150)).replace(day=1)

        start_date = parse_date_mixed(start) or default_start
        end_date   = parse_date_mixed(end)   or default_end

        with get_session_context() as session:
            revenue_service = RevenueService(session)
            rows, totals, chart_data = revenue_service.compute_monthly_report(start_date, end_date, group_by)
        
        # Convert dates to strings for template serialization
        rows_serializable = []
        for row in rows:
            row_copy = row.copy()
            if 'month' in row_copy and hasattr(row_copy['month'], 'strftime'):
                row_copy['month'] = row_copy['month'].strftime("%Y-%m")
            rows_serializable.append(row_copy)
        
        # Convert totals dict to match template expectations
        from types import SimpleNamespace
        template_totals = {
            "revenue_vnd": totals.get("total_revenue", 0),
            "sold_nights": totals.get("total_sold_nights", 0), 
            "vacant_nights": totals.get("total_vacant_nights", 0),
            "occupancy_pct": totals.get("total_occupancy_pct", 0.0),
            "revpar_vnd": totals.get("total_revpar_vnd", 0),
            "forecast_revenue_vnd": 0  # Placeholder for now
        }
        totals_obj = SimpleNamespace(**template_totals)
        
        # Convert chart_data to match template expectations
        template_chart = {
            "month_labels": chart_data.get("trend_months", []),
            "revenue_by_month": [int(d.get("revenue", 0)) for d in chart_data.get("trend_data", [])],
            "sold_nights_by_month": [d.get("sold_nights", 0) for d in chart_data.get("trend_data", [])],
            "occupancy_pct_by_month": [0] * len(chart_data.get("trend_months", [])),  # Placeholder
            "airbnb_revenue_by_month": chart_data.get("airbnb_monthly", []),
            "offline_revenue_by_month": chart_data.get("offline_monthly", []),
            "channel_labels": [item.get("channel", "") for item in chart_data.get("channel_pie", [])],
            "channel_revenue": [item.get("revenue", 0) for item in chart_data.get("channel_pie", [])]
        }

        # ---------- PHÂN TRANG ----------
        total_rows = len(rows_serializable)
        pages = max(1, math.ceil(total_rows / page_size))
        page = min(max(1, p), pages)

        start_idx = (page - 1) * page_size
        end_idx   = min(start_idx + page_size, total_rows)
        rows_page = rows_serializable[start_idx:end_idx]

        pagination = {
            "page": page,
            "page_size": page_size,
            "total": total_rows,
            "pages": pages,
            "start": (start_idx + 1) if total_rows else 0,
            "end": end_idx,
        }

        return templates.TemplateResponse("reports_monthly.html", {
            "request": request,
            "rows": rows_page,          # chỉ trả trang hiện tại
            "start": start_date.strftime("%Y-%m-%d"),  # Convert to string
            "end": end_date.strftime("%Y-%m-%d"),      # Convert to string
            "group_by": group_by,
            "totals": totals_obj,       # Use object format for template
            "chart": template_chart,    # Use converted chart format
            "geo_data": [],  # Tạm thời để trống, có thể thêm sau
            "pagination": pagination,   # thông tin phân trang
        })
        
    except Exception as e:
        # Debug: Trả về lỗi cụ thể
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in report_monthly: {e}")
        print(f"📋 Full traceback:\n{error_details}")
        
        return HTMLResponse(
            content=f"<h1>Debug Error</h1><pre>{error_details}</pre>", 
            status_code=500
        )

# ================= MISSING ROUTES - BUILDINGS & PROPERTIES =================

@app.get("/buildings", response_class=HTMLResponse)
async def show_buildings(request: Request):
    with get_session_context() as session:
        property_service = PropertyService(session)
        building_data = property_service.get_buildings_with_counts()

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
    with get_session_context() as session:
        new_building = Building(
            building_name=building_name,
            building_code=building_code,
            address=address
        )
        session.add(new_building)
        session.commit()
    return RedirectResponse(url="/buildings", status_code=303)

@app.get("/properties", response_class=HTMLResponse)
async def show_properties(request: Request):
    with get_session_context() as session:
        property_service = PropertyService(session)
        properties = property_service.get_properties_with_buildings()

    return templates.TemplateResponse("properties.html", {
        "request": request,
        "properties": properties
    })

# API endpoints for AJAX
@app.get("/api/buildings")
async def api_buildings():
    with get_session_context() as session:
        buildings = session.exec(select(Building)).all()
        return [{"id": b.id, "name": b.building_name} for b in buildings]

@app.get("/api/properties")
async def api_properties():
    with get_session_context() as session:
        properties = session.exec(select(Property)).all()
        return [{"id": p.id, "name": p.property_name, "building_id": p.building_id} for p in properties]

@app.post("/api/csv/preview")
async def api_csv_preview(
    files: List[UploadFile] = File(...),
    room_mapping: Optional[str] = Form(None)
):
    """Preview CSV files với room mapping để kiểm tra trước khi upload."""
    try:
        # Parse room mapping data if provided
        room_mapping_data = None
        if room_mapping:
            import json
            room_mapping_data = json.loads(room_mapping)
        
        # Get room mapping preview from utils
        from utils import get_room_mapping_preview
        preview_data = []
        
        for upload_file in files:
            content = await upload_file.read()
            df = pd.read_csv(io.BytesIO(content))
            
            # Get preview for this file
            file_preview = get_room_mapping_preview(df, room_mapping_data)
            preview_data.append({
                "filename": upload_file.filename,
                "preview": file_preview
            })
            
            # Reset file pointer
            await upload_file.seek(0)
        
        return {"success": True, "data": preview_data}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/csv/preview-json")
async def api_csv_preview_json(data: dict):
    """Preview CSV với JSON data để test."""
    try:
        from utils import get_room_mapping_preview
        import io
        
        csv_content = data.get('csv_content', '')
        room_mapping_data = data.get('room_mapping')
        
        # Parse CSV from string content
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Get preview
        preview = get_room_mapping_preview(df, room_mapping_data)
        
        return {"success": True, "preview": preview}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# Calendar Route
@app.get("/calendar", response_class=HTMLResponse)
def show_calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})
