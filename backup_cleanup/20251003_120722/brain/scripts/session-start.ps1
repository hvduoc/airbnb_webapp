# 🚀 SESSION START - Airbnb Revenue WebApp
# Mục tiêu: Load context cho AI mỗi ca làm việc

Write-Host ""
Write-Host "🧠 ============================================" -ForegroundColor Cyan
Write-Host "   AIRBNB REVENUE WEBAPP - SESSION START" -ForegroundColor White
Write-Host "🧠 ============================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra brain system
if (-not (Test-Path ".brain")) {
    Write-Host "❌ KHÔNG TÌM THẤY BỘ NÃO SYSTEM!" -ForegroundColor Red
    Write-Host "Chạy script setup trước khi bắt đầu." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Bộ não system đã sẵn sàng" -ForegroundColor Green

# Hiển thị project context
Write-Host ""
Write-Host "📋 PROJECT CONTEXT:" -ForegroundColor Yellow
Write-Host "   • Domain: PMS (Property Management System)" -ForegroundColor White  
Write-Host "   • Tech Stack: FastAPI + SQLAlchemy + Jinja2" -ForegroundColor White
Write-Host "   • Focus: Airbnb booking management & revenue reporting" -ForegroundColor White

# Load và hiển thị active tasks
if (Test-Path ".brain/tasks/ACTIVE_TASKS.json") {
    try {
        $tasks = Get-Content ".brain/tasks/ACTIVE_TASKS.json" | ConvertFrom-Json
        $activeCount = $tasks.active_tasks.Count
        $inProgressCount = ($tasks.active_tasks | Where-Object { $_.status -eq "In Progress" }).Count
        
        Write-Host ""
        Write-Host "📝 ACTIVE TASKS:" -ForegroundColor Yellow  
        Write-Host "   • Total: $activeCount tasks" -ForegroundColor White
        Write-Host "   • In Progress: $inProgressCount tasks" -ForegroundColor White
        
        if ($inProgressCount -gt 0) {
            Write-Host ""
            Write-Host "🔄 CURRENT PRIORITIES:" -ForegroundColor Cyan
            $tasks.active_tasks | Where-Object { $_.status -eq "In Progress" } | ForEach-Object {
                Write-Host "   • $($_.title) ($($_.priority) priority)" -ForegroundColor White
            }
        }
    }
    catch {
        Write-Host "   ⚠️ Lỗi đọc ACTIVE_TASKS.json" -ForegroundColor Yellow
    }
}

# Hiển thị recent daily logs
$todayLog = ".brain/logs/daily/$(Get-Date -Format 'yyyy-MM-dd').md"
if (Test-Path $todayLog) {
    Write-Host ""
    Write-Host "📅 Daily log hôm nay đã tồn tại" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "📅 Chưa có daily log hôm nay - nên tạo entry mới" -ForegroundColor Yellow
}

# Context prompt cho AI
Write-Host ""
Write-Host "🤖 AI CONTEXT PROMPT:" -ForegroundColor Magenta
Write-Host "────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "Bạn đang ở trong dự án Airbnb Revenue WebApp - một PMS system" -ForegroundColor White
Write-Host "để quản lý booking và revenue từ Airbnb." -ForegroundColor White
Write-Host ""
Write-Host "Context: Đọc .brain/SCOPE.md và .brain/tasks/ACTIVE_TASKS.json" -ForegroundColor White
Write-Host "để hiểu current priorities." -ForegroundColor White
Write-Host ""
Write-Host "Tech stack: FastAPI + SQLAlchemy + Jinja2 templates." -ForegroundColor White
Write-Host ""
Write-Host "Bạn có hiểu project scope, current tasks, và technical context không?" -ForegroundColor White
Write-Host "────────────────────────────────────────────────────────────" -ForegroundColor Gray

Write-Host ""
Write-Host "🚀 SẴN SÀNG LÀM VIỆC!" -ForegroundColor Green
Write-Host ""