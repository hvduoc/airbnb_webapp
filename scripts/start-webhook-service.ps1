# Khởi động GitHub Webhook Sync Service
# start-webhook-service.ps1

param(
    [int]$Port = 8002,
    [switch]$Development,
    [switch]$Background
)

Write-Host "🚀 Starting GitHub Webhook Sync Service..." -ForegroundColor Green

# Kiểm tra Python
try {
    $PythonVersion = python --version 2>&1
    Write-Host "✅ Python: $PythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Kiểm tra dependencies
if (-not (Test-Path "webhook-requirements.txt")) {
    Write-Host "❌ webhook-requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Cài đặt dependencies nếu cần
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r webhook-requirements.txt

# Kiểm tra file .env.webhook
if (-not (Test-Path ".env.webhook")) {
    Write-Host "⚠️ .env.webhook not found, using default values" -ForegroundColor Yellow
    Write-Host "🔧 Please copy .env.webhook.example to .env.webhook and configure" -ForegroundColor Yellow
}

# Load environment variables từ .env.webhook
if (Test-Path ".env.webhook") {
    Get-Content ".env.webhook" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.+)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Tạo thư mục logs
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

# Command để chạy service
$Command = "python webhook_listener.py"

if ($Development) {
    $Command = "uvicorn webhook_listener:app --reload --host 0.0.0.0 --port $Port"
}

# Hiển thị thông tin
Write-Host ""
Write-Host "🔗 Service will be available at:" -ForegroundColor Cyan
Write-Host "   http://localhost:$Port" -ForegroundColor White
Write-Host "   http://localhost:$Port/api/webhook (GitHub webhook endpoint)" -ForegroundColor White
Write-Host "   http://localhost:$Port/api/sync/status (Sync status)" -ForegroundColor White
Write-Host ""
Write-Host "📝 Logs will be saved to:" -ForegroundColor Cyan
Write-Host "   webhook_sync.log (Application logs)" -ForegroundColor White
Write-Host "   sync_history.json (Sync history)" -ForegroundColor White
Write-Host ""

if ($Background) {
    Write-Host "🎯 Starting service in background..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Command -WindowStyle Minimized
}
else {
    Write-Host "🎯 Starting service..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    Invoke-Expression $Command
}