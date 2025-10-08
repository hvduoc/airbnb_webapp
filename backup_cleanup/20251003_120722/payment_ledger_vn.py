"""
Hệ thống Quản lý Thu Chi Airbnb - Phiên bản Việt Nam
Bao gồm tính năng bàn giao, đính kèm hình ảnh, dấu thời gian
"""

import os
import shutil
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Thiết lập lưu trữ file
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Lưu trữ đơn giản cho demo
payments_db = []
handovers_db = []
users_db = {
    "assistant": {"password": "assistant123", "role": "assistant", "name": "Trợ lý"},
    "manager": {"password": "manager123", "role": "manager", "name": "Quản lý"},
    "owner": {"password": "owner123", "role": "owner", "name": "Chủ sở hữu"},
}
current_sessions = {}

# Danh sách người nhận có thể bàn giao
recipients = [
    {
        "id": "nguyen_van_a",
        "name": "Nguyễn Văn A",
        "role": "Trợ lý",
        "phone": "0901234567",
    },
    {
        "id": "tran_thi_b",
        "name": "Trần Thị B",
        "role": "Quản lý",
        "phone": "0902345678",
    },
    {"id": "le_van_c", "name": "Lê Văn C", "role": "Kế toán", "phone": "0903456789"},
    {
        "id": "pham_thi_d",
        "name": "Phạm Thị D",
        "role": "Chủ sở hữu",
        "phone": "0904567890",
    },
]

app = FastAPI(
    title="Hệ thống Thu Chi Airbnb", description="Quản lý thu chi và bàn giao tiền mặt"
)
templates = Jinja2Templates(directory="templates")

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# Xác thực đơn giản
def authenticate_user(username: str, password: str):
    """Xác thực người dùng"""
    user = users_db.get(username)
    if user and user["password"] == password:
        return user
    return None


def get_current_user(request: Request):
    """Lấy thông tin người dùng hiện tại"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in current_sessions:
        return current_sessions[session_id]
    raise HTTPException(status_code=401, detail="Chưa đăng nhập")


# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Trang chủ"""
    return templates.TemplateResponse("payment_ledger_vn.html", {"request": request})


@app.post("/api/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Đăng nhập"""
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Thông tin đăng nhập không đúng")

    # Tạo session đơn giản
    session_id = f"{username}_{datetime.now().timestamp()}"
    current_sessions[session_id] = user

    response = JSONResponse({"success": True, "user": user})
    response.set_cookie("session_id", session_id, httponly=True)
    return response


@app.post("/api/payments")
async def add_payment(
    request: Request,
    booking_id: str = Form(...),
    guest_name: str = Form(...),
    amount_due: float = Form(...),
    amount_collected: float = Form(...),
    payment_method: str = Form(...),
    collected_by: str = Form(...),
    notes: str = Form(default=""),
    receipt_image: Optional[UploadFile] = File(None),
):
    """Thêm khoản thu mới"""
    current_user = get_current_user(request)

    # Xử lý upload hình ảnh
    image_path = None
    if receipt_image and receipt_image.filename:
        # Tạo tên file unique
        file_extension = receipt_image.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        image_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Lưu file
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(receipt_image.file, buffer)

        image_path = f"/uploads/{unique_filename}"

    payment = {
        "id": len(payments_db) + 1,
        "timestamp": datetime.now().isoformat(),
        "booking_id": booking_id,
        "guest_name": guest_name,
        "amount_due": amount_due,
        "amount_collected": amount_collected,
        "payment_method": payment_method,
        "collected_by": collected_by,
        "notes": notes,
        "status": "completed",
        "added_by": current_user["name"],
        "receipt_image": image_path,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }

    payments_db.append(payment)

    return {"success": True, "payment": payment}


@app.get("/api/payments")
async def get_payments(request: Request):
    """Lấy danh sách khoản thu"""
    current_user = get_current_user(request)

    # Lọc theo vai trò
    if current_user["role"] == "assistant":
        # Trợ lý chỉ xem được khoản thu của mình
        filtered_payments = [
            p for p in payments_db if p["collected_by"] == current_user["name"].lower()
        ]
    else:
        # Quản lý và chủ sở hữu xem được tất cả
        filtered_payments = payments_db

    return {"payments": filtered_payments}


@app.get("/api/dashboard")
async def get_dashboard(request: Request):
    """Lấy thông tin dashboard"""
    get_current_user(request)

    total_collected = sum(p["amount_collected"] for p in payments_db)
    total_due = sum(p["amount_due"] for p in payments_db)
    collection_rate = (total_collected / total_due * 100) if total_due > 0 else 0

    # Tính tiền mặt cần bàn giao (giả sử 60% là tiền mặt)
    cash_payments = sum(
        p["amount_collected"] for p in payments_db if p["payment_method"] == "cash"
    )
    cash_handed_over = sum(
        h["amount"] for h in handovers_db if h["status"] == "completed"
    )
    cash_pending = cash_payments - cash_handed_over

    return {
        "total_collected": total_collected,
        "total_due": total_due,
        "collection_rate": round(collection_rate, 2),
        "total_payments": len(payments_db),
        "cash_balance": cash_payments,
        "cash_pending_handover": cash_pending,
        "total_handovers": len(handovers_db),
        "last_updated": datetime.now().isoformat(),
    }


@app.post("/api/handovers")
async def create_handover(
    request: Request,
    recipient_id: str = Form(...),
    amount: float = Form(...),
    notes: str = Form(default=""),
    handover_image: Optional[UploadFile] = File(None),
):
    """Tạo bàn giao tiền mặt"""
    current_user = get_current_user(request)

    # Tìm thông tin người nhận
    recipient = next((r for r in recipients if r["id"] == recipient_id), None)
    if not recipient:
        raise HTTPException(status_code=400, detail="Không tìm thấy người nhận")

    # Xử lý upload hình ảnh bàn giao
    image_path = None
    if handover_image and handover_image.filename:
        file_extension = handover_image.filename.split(".")[-1]
        unique_filename = f"handover_{uuid.uuid4()}.{file_extension}"
        image_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(handover_image.file, buffer)

        image_path = f"/uploads/{unique_filename}"

    handover = {
        "id": len(handovers_db) + 1,
        "timestamp": datetime.now().isoformat(),
        "handover_by": current_user["name"],
        "recipient_id": recipient_id,
        "recipient_name": recipient["name"],
        "recipient_phone": recipient["phone"],
        "amount": amount,
        "notes": notes,
        "status": "completed",
        "handover_image": image_path,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "signature_status": "pending",  # Trạng thái ký nhận
    }

    handovers_db.append(handover)

    return {"success": True, "handover": handover}


@app.get("/api/handovers")
async def get_handovers(request: Request):
    """Lấy danh sách bàn giao"""
    get_current_user(request)

    return {"handovers": handovers_db}


@app.get("/api/recipients")
async def get_recipients(request: Request):
    """Lấy danh sách người nhận"""
    get_current_user(request)

    return {"recipients": recipients}


@app.post("/api/logout")
async def logout(request: Request):
    """Đăng xuất"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in current_sessions:
        del current_sessions[session_id]

    response = JSONResponse({"success": True})
    response.delete_cookie("session_id")
    return response


# Thêm dữ liệu demo
payments_db.extend(
    [
        {
            "id": 1,
            "timestamp": "2025-09-30T10:00:00",
            "booking_id": "BK001",
            "guest_name": "Nguyễn Văn Minh",
            "amount_due": 1000000,
            "amount_collected": 1000000,
            "payment_method": "cash",
            "collected_by": "assistant",
            "notes": "Thu đầy đủ tiền mặt",
            "status": "completed",
            "added_by": "Trợ lý",
            "receipt_image": None,
            "created_at": "30/09/2025 10:00:00",
        },
        {
            "id": 2,
            "timestamp": "2025-09-30T11:30:00",
            "booking_id": "BK002",
            "guest_name": "Trần Thị Lan",
            "amount_due": 1500000,
            "amount_collected": 1500000,
            "payment_method": "bank_transfer",
            "collected_by": "manager",
            "notes": "Chuyển khoản đã xác nhận",
            "status": "completed",
            "added_by": "Quản lý",
            "receipt_image": None,
            "created_at": "30/09/2025 11:30:00",
        },
    ]
)

handovers_db.extend(
    [
        {
            "id": 1,
            "timestamp": "2025-09-30T15:00:00",
            "handover_by": "Trợ lý",
            "recipient_id": "tran_thi_b",
            "recipient_name": "Trần Thị B",
            "recipient_phone": "0902345678",
            "amount": 500000,
            "notes": "Bàn giao tiền mặt cuối ngày",
            "status": "completed",
            "handover_image": None,
            "created_at": "30/09/2025 15:00:00",
            "signature_status": "signed",
        }
    ]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
