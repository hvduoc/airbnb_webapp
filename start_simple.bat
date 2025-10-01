@echo off
echo.
echo ==========================================
echo   Payment Ledger - Quick Start
echo ==========================================
echo.

echo [1/4] Installing Python dependencies...
pip install fastapi uvicorn sqlmodel passlib[bcrypt] PyJWT python-multipart
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Creating demo users...
python create_payment_users.py
if %errorlevel% neq 0 (
    echo WARNING: Demo users creation failed - will retry after server starts
)

echo.
echo [3/4] Starting FastAPI server...
echo.
echo ==========================================
echo   Server starting at: http://localhost:8000
echo   Payment Login: http://localhost:8000/payments/login
echo   API Docs: http://localhost:8000/docs
echo ==========================================
echo.
echo Demo Accounts:
echo   Assistant: assistant / assistant123
echo   Manager:   manager   / manager123
echo   Owner:     owner     / owner123
echo.
echo Press Ctrl+C to stop server
echo ==========================================
echo.

echo [4/4] Launching server...
uvicorn main:app --reload

pause