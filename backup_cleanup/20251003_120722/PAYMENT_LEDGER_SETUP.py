# Payment Ledger Module - Setup and Requirements

"""
This file contains the installation and setup instructions for the Payment Ledger module
that integrates with Google Sheets API.
"""

REQUIREMENTS = """
# Additional requirements for Payment Ledger module

# Google Sheets API
gspread==5.12.0
google-auth==2.24.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1

# JWT Authentication
PyJWT==2.8.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Async support
asyncio-mqtt==0.16.1
"""

ENVIRONMENT_VARIABLES = """
# Add these to your .env file:

# Google Sheets API Configuration
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id_here

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production

# Payment System Configuration
PAYMENT_CURRENCY=VND
PAYMENT_TIMEZONE=Asia/Ho_Chi_Minh
"""

GOOGLE_SHEETS_SETUP = """
# Google Sheets API Setup Instructions

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name: "payment-ledger-service"
   - Download JSON credentials file
5. Share Google Sheets with service account email
6. Place credentials file in: credentials/service-account.json
"""

DATABASE_MIGRATION = """
# Database migration for user authentication

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    last_login DATETIME DEFAULT NULL,
    accessible_properties TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS usersession (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_jti VARCHAR UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    ip_address VARCHAR DEFAULT NULL,
    user_agent VARCHAR DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_usersession_user_id ON usersession(user_id);
CREATE INDEX idx_usersession_token ON usersession(token_jti);
"""

DEMO_USERS = """
# Demo users for testing (run this script to create)

from passlib.context import CryptContext
from sqlmodel import Session
from db import get_session
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_demo_users():
    session = Session()
    
    users = [
        {
            "username": "assistant",
            "email": "assistant@example.com",
            "full_name": "Trợ lý",
            "password": "assistant123",
            "role": "user"
        },
        {
            "username": "manager", 
            "email": "manager@example.com",
            "full_name": "Quản lý",
            "password": "manager123",
            "role": "manager"
        },
        {
            "username": "owner",
            "email": "owner@example.com", 
            "full_name": "Chủ",
            "password": "owner123",
            "role": "admin"
        }
    ]
    
    for user_data in users:
        # Check if user already exists
        existing = session.query(User).filter(
            User.username == user_data["username"]
        ).first()
        
        if existing:
            print(f"User {user_data['username']} already exists")
            continue
            
        # Create new user
        hashed_password = pwd_context.hash(user_data["password"])
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=hashed_password,
            role=user_data["role"],
            is_active=True,
            is_verified=True
        )
        
        session.add(user)
        print(f"Created user: {user_data['username']}")
    
    session.commit()
    session.close()
    print("Demo users created successfully!")

if __name__ == "__main__":
    create_demo_users()
"""

INTEGRATION_INSTRUCTIONS = """
# Integration with main.py

1. Add imports to main.py:
```python
from routes_payments import router as payments_router
from auth.auth_service import auth_router
from services.google_sheets.service import sheets_service
```

2. Add routers to FastAPI app:
```python
app.include_router(auth_router)
app.include_router(payments_router)
```

3. Add startup event to initialize Google Sheets:
```python
@app.on_event("startup")
async def startup_event():
    await sheets_service.initialize()
```

4. Add template routes:
```python
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("payments/login.html", {"request": request})

@app.get("/payments/dashboard", response_class=HTMLResponse)
async def payments_dashboard(request: Request):
    return templates.TemplateResponse("payments/dashboard.html", {"request": request})
```
"""

TESTING_CHECKLIST = """
# Testing Checklist

## Backend API Testing
- [ ] POST /api/auth/login - User authentication
- [ ] GET /api/auth/me - Get current user
- [ ] POST /api/payments/add - Add payment record
- [ ] GET /api/payments/list - List payments with filters
- [ ] POST /api/payments/cashflow/handover - Cash handover
- [ ] GET /api/payments/cashflow/list - Cashflow history
- [ ] GET /api/payments/dashboard - Dashboard metrics
- [ ] GET /api/payments/dashboard/revenue-by-period - Revenue charts
- [ ] GET /api/payments/dashboard/collector-performance - Performance metrics

## Google Sheets Integration
- [ ] Service account authentication
- [ ] Create sheets if not exist
- [ ] Add payment records to Payments sheet
- [ ] Add cashflow records to Cashflow sheet
- [ ] Read data from sheets with filters
- [ ] Handle API rate limits and errors

## Frontend Testing
- [ ] Login page functionality
- [ ] Role-based access control
- [ ] Payment form validation and submission
- [ ] Payments list with filtering
- [ ] Cash handover form (Manager/Owner only)
- [ ] Dashboard charts and KPIs
- [ ] Real-time data updates
- [ ] Responsive design on mobile

## Security Testing
- [ ] JWT token validation
- [ ] Role-based route protection
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
"""

print("Payment Ledger setup instructions ready!")
print("Next steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Setup Google Sheets API credentials")
print("3. Create demo users")
print("4. Integrate with main.py")
print("5. Test all functionality")