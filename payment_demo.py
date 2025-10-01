"""
Standalone Payment Ledger Demo
Simple payment tracking system that works without complex dependencies
"""

from fastapi import FastAPI, Request, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

# Simple in-memory storage for demo
payments_db = []
users_db = {
    "assistant": {"password": "assistant123", "role": "assistant", "name": "Assistant"},
    "manager": {"password": "manager123", "role": "manager", "name": "Manager"},
    "owner": {"password": "owner123", "role": "owner", "name": "Owner"}
}
current_sessions = {}

app = FastAPI(title="Payment Ledger Demo", description="Simple payment tracking system")
templates = Jinja2Templates(directory="templates")

# Simple authentication
def authenticate_user(username: str, password: str):
    """Simple authentication without JWT"""
    user = users_db.get(username)
    if user and user["password"] == password:
        return user
    return None

def get_current_user(request: Request):
    """Get current user from session"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in current_sessions:
        return current_sessions[session_id]
    raise HTTPException(status_code=401, detail="Not authenticated")

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to payment login"""
    return templates.TemplateResponse("payment_demo.html", {"request": request})

@app.post("/api/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Simple login endpoint"""
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create simple session
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
    notes: str = Form(default="")
):
    """Add a new payment record"""
    current_user = get_current_user(request)
    
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
        "added_by": current_user["name"]
    }
    
    payments_db.append(payment)
    
    return {"success": True, "payment": payment}

@app.get("/api/payments")
async def get_payments(request: Request):
    """Get all payments"""
    current_user = get_current_user(request)
    
    # Filter by role
    if current_user["role"] == "assistant":
        # Assistants only see their own payments
        filtered_payments = [p for p in payments_db if p["collected_by"] == current_user["name"].lower()]
    else:
        # Managers and owners see all payments
        filtered_payments = payments_db
    
    return {"payments": filtered_payments}

@app.get("/api/dashboard")
async def get_dashboard(request: Request):
    """Get dashboard metrics"""
    current_user = get_current_user(request)
    
    total_collected = sum(p["amount_collected"] for p in payments_db)
    total_due = sum(p["amount_due"] for p in payments_db)
    collection_rate = (total_collected / total_due * 100) if total_due > 0 else 0
    
    return {
        "total_collected": total_collected,
        "total_due": total_due,
        "collection_rate": round(collection_rate, 2),
        "total_payments": len(payments_db),
        "cash_balance": total_collected * 0.6,  # Demo calculation
        "last_updated": datetime.now().isoformat()
    }

@app.post("/api/logout")
async def logout(request: Request):
    """Logout user"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in current_sessions:
        del current_sessions[session_id]
    
    response = JSONResponse({"success": True})
    response.delete_cookie("session_id")
    return response

# Add some demo data
payments_db.extend([
    {
        "id": 1,
        "timestamp": "2025-09-30T10:00:00",
        "booking_id": "BK001",
        "guest_name": "John Doe",
        "amount_due": 1000000,
        "amount_collected": 1000000,
        "payment_method": "cash",
        "collected_by": "assistant",
        "notes": "Full payment received",
        "status": "completed",
        "added_by": "Assistant"
    },
    {
        "id": 2,
        "timestamp": "2025-09-30T11:30:00",
        "booking_id": "BK002",
        "guest_name": "Jane Smith",
        "amount_due": 1500000,
        "amount_collected": 1500000,
        "payment_method": "bank_transfer",
        "collected_by": "manager",
        "notes": "Bank transfer confirmed",
        "status": "completed",
        "added_by": "Manager"
    }
])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)