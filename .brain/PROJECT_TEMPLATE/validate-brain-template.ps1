# 🔍 VALIDATE BRAIN TEMPLATE - PowerShell Script
# Mục tiêu: Kiểm tra brain system sau khi setup từ template

param(
    [Parameter(Mandatory = $false)]
    [string]$BrainPath = ".brain"
)

# Màu sắc output
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️ $msg" -ForegroundColor Cyan }

Write-Info "🔍 BẮT ĐẦU VALIDATION BRAIN TEMPLATE SYSTEM"
Write-Info "📁 Kiểm tra thư mục: $BrainPath"

# Tracking results
$results = @{
    "files_checked" = 0
    "passed"        = 0
    "warnings"      = 0
    "failed"        = 0
    "issues"        = @()
}

function Add-Result {
    param($status, $message, $details = "")
    
    $results["files_checked"]++
    
    switch ($status) {
        "PASS" { 
            $results["passed"]++
            Write-Success "$message"
        }
        "WARN" { 
            $results["warnings"]++
            Write-Warning "$message"
            if ($details) { $results["issues"] += "WARNING: $message - $details" }
        }
        "FAIL" { 
            $results["failed"]++
            Write-Error "$message"
            $results["issues"] += "FAILED: $message - $details"
        }
    }
}

Write-Info ""
Write-Info "📋 **KIỂM TRA CẤU TRÚC THU MỤC**"

# Kiểm tra brain directory tồn tại
if (-not (Test-Path $BrainPath)) {
    Add-Result "FAIL" "Brain directory không tồn tại: $BrainPath" "Run create-brain-from-template script first"
    Write-Info "🚨 VALIDATION STOPPED - Không tìm thấy brain system"
    exit 1
}

Add-Result "PASS" "Brain directory tồn tại: $BrainPath"

# Kiểm tra các thư mục bắt buộc
$requiredDirs = @("tasks", "context", "logs/daily")
foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $BrainPath $dir
    if (Test-Path $fullPath) {
        Add-Result "PASS" "Thư mục required: $dir"
    }
    else {
        Add-Result "FAIL" "Thiếu thư mục: $dir" "Create missing directory structure"
    }
}

Write-Info ""
Write-Info "📄 **KIỂM TRA FILES CỐT LÕI**"

# Kiểm tra core files
$coreFiles = @{
    "SCOPE.md"                 = "Project scope definition"
    "tasks/ACTIVE_TASKS.json"  = "Active tasks tracking"  
    "context/CONTEXT_INDEX.md" = "Context index"
}

foreach ($file in $coreFiles.Keys) {
    $filePath = Join-Path $BrainPath $file
    $description = $coreFiles[$file]
    
    if (Test-Path $filePath) {
        Add-Result "PASS" "File tồn tại: $file ($description)"
    }
    else {
        Add-Result "FAIL" "Thiếu file: $file" $description
    }
}

Write-Info ""
Write-Info "🔧 **KIỂM TRA JSON SYNTAX**"

# Kiểm tra ACTIVE_TASKS.json syntax
$jsonPath = Join-Path $BrainPath "tasks/ACTIVE_TASKS.json"
if (Test-Path $jsonPath) {
    try {
        $jsonContent = Get-Content $jsonPath -Raw | ConvertFrom-Json
        Add-Result "PASS" "JSON syntax hợp lệ: ACTIVE_TASKS.json"
        
        # Kiểm tra required fields trong JSON
        if ($jsonContent.project) {
            Add-Result "PASS" "JSON có project metadata"
        }
        else {
            Add-Result "WARN" "JSON thiếu project metadata" "Add project info to JSON"
        }
        
        if ($jsonContent.active_tasks -and $jsonContent.active_tasks.Count -gt 0) {
            Add-Result "PASS" "JSON có active tasks ($($jsonContent.active_tasks.Count) tasks)"
        }
        else {
            Add-Result "WARN" "JSON không có active tasks" "Add initial tasks to get started"
        }
        
    }
    catch {
        Add-Result "FAIL" "JSON syntax không hợp lệ: ACTIVE_TASKS.json" $_.Exception.Message
    }
}
else {
    Add-Result "FAIL" "Không tìm thấy ACTIVE_TASKS.json" "Create tasks file"
}

Write-Info ""
Write-Info "🏷️ **KIỂM TRA PLACEHOLDERS**"

# Kiểm tra placeholders chưa thay trong các file
$filesToCheck = @("SCOPE.md", "DOMAIN_MAP.md", "README.md", "context/CONTEXT_INDEX.md")
$placeholderPattern = '\{\{[^}]+\}\}'

foreach ($file in $filesToCheck) {
    $filePath = Join-Path $BrainPath $file
    
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        $matches = [regex]::Matches($content, $placeholderPattern)
        
        if ($matches.Count -eq 0) {
            Add-Result "PASS" "Không còn placeholder: $file"
        }
        else {
            $placeholderList = ($matches | ForEach-Object { $_.Value }) -join ", "
            Add-Result "WARN" "Còn $($matches.Count) placeholder trong: $file" "Placeholders: $placeholderList"
        }
    }
}

Write-Info ""
Write-Info "📅 **KIỂM TRA LOGS**"

# Kiểm tra có daily log không
$today = Get-Date -Format "yyyy-MM-dd"
$todayLogPath = Join-Path $BrainPath "logs/daily/$today.md"

if (Test-Path $todayLogPath) {
    Add-Result "PASS" "Daily log tồn tại: $today.md"
}
else {
    Add-Result "WARN" "Chưa có daily log hôm nay: $today.md" "Create daily log entry"
}

Write-Info ""
Write-Info "🎯 **KẾT QUẢ VALIDATION**"

# Hiển thị bảng kết quả
Write-Host "┌─────────────────────────────────────────────┐" -ForegroundColor Gray
Write-Host "│" -NoNewline -ForegroundColor Gray
Write-Host "              VALIDATION SUMMARY              " -NoNewline -ForegroundColor White  
Write-Host "│" -ForegroundColor Gray
Write-Host "├─────────────────────────────────────────────┤" -ForegroundColor Gray

$passColor = if ($results["passed"] -gt 0) { "Green" } else { "Gray" }
$warnColor = if ($results["warnings"] -gt 0) { "Yellow" } else { "Gray" }  
$failColor = if ($results["failed"] -gt 0) { "Red" } else { "Gray" }

Write-Host "│ " -NoNewline -ForegroundColor Gray
Write-Host "✅ PASSED: " -NoNewline -ForegroundColor $passColor
Write-Host ("{0,2}" -f $results["passed"]) -NoNewline -ForegroundColor $passColor
Write-Host " │ " -NoNewline -ForegroundColor Gray
Write-Host "⚠️ WARNINGS: " -NoNewline -ForegroundColor $warnColor  
Write-Host ("{0,2}" -f $results["warnings"]) -NoNewline -ForegroundColor $warnColor
Write-Host " │ " -NoNewline -ForegroundColor Gray
Write-Host "❌ FAILED: " -NoNewline -ForegroundColor $failColor
Write-Host ("{0,2}" -f $results["failed"]) -NoNewline -ForegroundColor $failColor
Write-Host " │" -ForegroundColor Gray

Write-Host "└─────────────────────────────────────────────┘" -ForegroundColor Gray

# Overall status
$overallStatus = if ($results["failed"] -gt 0) { "FAILED" } 
elseif ($results["warnings"] -gt 0) { "WARNINGS" } 
else { "PASSED" }

switch ($overallStatus) {
    "PASSED" { 
        Write-Success "🎉 BRAIN TEMPLATE VALIDATION PASSED!"
        Write-Info "Brain system đã sẵn sàng sử dụng."
    }
    "WARNINGS" { 
        Write-Warning "⚠️ BRAIN TEMPLATE CÓ WARNINGS"  
        Write-Info "System có thể dùng được nhưng nên khắc phục warnings."
    }
    "FAILED" { 
        Write-Error "❌ BRAIN TEMPLATE VALIDATION FAILED"
        Write-Info "Cần khắc phục lỗi trước khi sử dụng system."
    }
}

# Hiển thị issues nếu có
if ($results["issues"].Count -gt 0) {
    Write-Info ""
    Write-Info "🔧 **ISSUES CẦN KHẮC PHỤC**:"
    foreach ($issue in $results["issues"]) {
        Write-Host "  • $issue" -ForegroundColor Yellow
    }
}

Write-Info ""
Write-Info "📊 Tổng số items kiểm tra: $($results["files_checked"])"

# Return exit code
if ($results["failed"] -gt 0) {
    exit 1
}
else {
    exit 0
}