# 🚀 Payment Ledger - Quick Start Guide

## What is this?
A simple payment tracking system for managing Airbnb payment collections. Works immediately without any complex setup!

## 🎯 Super Quick Demo (30 seconds)

### Option 1: Simple Standalone Demo
```bash
python payment_demo.py
```
**Then open**: http://localhost:8001

### Option 2: Full System with Main App
```bash
uvicorn main:app --reload
```
**Then open**: http://localhost:8000

---

## 🎮 How to Use the Demo

### 1. Open Browser
- **Simple Demo**: http://localhost:8001
- **Full System**: http://localhost:8000

### 2. Login with Demo Account
Choose any of these accounts:
- **Assistant**: `assistant` / `assistant123` (can record payments)
- **Manager**: `manager` / `manager123` (can view all payments + reports)  
- **Owner**: `owner` / `owner123` (full access)

### 3. Try the Features
1. **Dashboard**: See payment statistics and metrics
2. **Add Payment**: Record a new payment transaction
3. **Payment History**: View all payment records

---

## 📋 Demo Payment Example

Try adding this payment:
- **Booking ID**: `BK003`
- **Guest Name**: `Test Guest`
- **Amount Due**: `2000000` (2M VND)
- **Amount Collected**: `2000000`
- **Payment Method**: `cash`
- **Collected By**: `assistant`
- **Notes**: `Test payment from demo`

---

## 🚀 Features Available

✅ **User Authentication** (3 role levels)  
✅ **Payment Recording** with validation  
✅ **Real-time Dashboard** with metrics  
✅ **Payment History** with filtering  
✅ **Role-based Access Control**  
✅ **Responsive Mobile Interface**  
✅ **No Database Setup Required** (uses memory storage)

---

## 🔧 For Production Use

If you want to use this for real business with Google Sheets:

### 1. Install Full Dependencies
```bash
pip install -r requirements_payments.txt
```

### 2. Setup Google Sheets (Optional)
See `credentials/README.md` for Google Sheets API setup

### 3. Create Real Users
```bash
python create_payment_users.py
```

### 4. Start Production Server
```bash
uvicorn main:app --reload
```

---

## � Screenshots & Demo

### Login Screen
- Simple authentication with demo accounts
- Clear role descriptions

### Dashboard
- KPI cards showing total collected, collection rate, cash balance
- Real-time updates when new payments added

### Add Payment Form
- Booking ID linking
- Multiple payment methods
- Validation and error handling

### Payment History
- Filterable list of all transactions
- Role-based visibility (assistants see only their payments)

---

## 🐛 Troubleshooting

### "Server not starting"
```bash
# Make sure you have Python and FastAPI
pip install fastapi uvicorn
python payment_demo.py
```

### "Can't access the page"
- Check if server is running
- Try http://localhost:8001 or http://localhost:8000
- Make sure firewall isn't blocking the port

### "Login not working"
- Use exact credentials: `assistant` / `assistant123`
- Check for typos in username/password

---

## 🎯 What's Different from Complex Version?

**Simple Demo** (`payment_demo.py`):
- ✅ Works immediately
- ✅ No external dependencies  
- ✅ In-memory storage (data resets on restart)
- ✅ Perfect for testing and demos

**Full System** (main Payment Ledger):
- ✅ Google Sheets integration
- ✅ Persistent data storage
- ✅ More advanced features
- ⚠️ Requires setup and configuration

---

## 🎉 Ready to Go!

**Just run `python payment_demo.py` and start using it immediately!**

No setup, no configuration, no database - just pure functionality for testing the Payment Ledger concept.

Perfect for:
- ✅ **Demos** to show clients
- ✅ **Testing** the interface and workflow  
- ✅ **Training** staff on the system
- ✅ **Development** and customization