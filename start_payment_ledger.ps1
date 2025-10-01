# Payment Ledger Quick Start Script
# Run this in PowerShell to set up and test the Payment Ledger module

Write-Host "🚀 Payment Ledger Quick Start" -ForegroundColor Green
Write-Host "=" * 50

# Check if Python is available
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Install requirements
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements_payments.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some dependencies may have failed to install" -ForegroundColor Yellow
}

# Run setup script
Write-Host "`n🔧 Running setup script..." -ForegroundColor Yellow
try {
    python setup_payment_ledger.py
    Write-Host "✅ Setup completed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Setup script encountered issues" -ForegroundColor Yellow
}

# Create demo users
Write-Host "`n👥 Creating demo users..." -ForegroundColor Yellow
try {
    python create_payment_users.py
    Write-Host "✅ Demo users created" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Demo users creation will run when server starts" -ForegroundColor Yellow
}

# Display next steps
Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Set up Google Sheets API (see credentials/README.md)" -ForegroundColor White
Write-Host "2. Update .env with your Google Spreadsheet ID" -ForegroundColor White  
Write-Host "3. Start server: uvicorn main:app --reload" -ForegroundColor White
Write-Host "4. Visit: http://localhost:8000/payments/login" -ForegroundColor White

Write-Host "`n🔑 Demo Credentials:" -ForegroundColor Cyan
Write-Host "Assistant: assistant / assistant123" -ForegroundColor White
Write-Host "Manager:   manager   / manager123" -ForegroundColor White
Write-Host "Owner:     owner     / owner123" -ForegroundColor White

Write-Host "`n🌟 Features Ready:" -ForegroundColor Cyan
Write-Host "✅ Payment recording with Google Sheets" -ForegroundColor Green
Write-Host "✅ Role-based access control" -ForegroundColor Green
Write-Host "✅ Cash handover management" -ForegroundColor Green
Write-Host "✅ Real-time analytics dashboard" -ForegroundColor Green
Write-Host "✅ Mobile-responsive interface" -ForegroundColor Green

Write-Host "`n🚀 Payment Ledger is ready to use!" -ForegroundColor Green

# Optional: Start server if user wants
$startServer = Read-Host "`nStart server now? (y/N)"
if ($startServer -eq "y" -or $startServer -eq "Y") {
    Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Green
    uvicorn main:app --reload
}