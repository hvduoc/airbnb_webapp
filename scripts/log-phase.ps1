# PowerShell Script để ghi log từng phase phát triển
# log-phase.ps1

param(
    [Parameter(Mandatory = $true)]
    [string]$PhaseNumber,
    
    [Parameter(Mandatory = $true)]
    [string]$PhaseName,
    
    [string]$Description = "",
    [string]$StartDate = "",
    [string]$EndDate = "",
    [array]$FilesChanged = @(),
    [array]$TasksUpdated = @(),
    [string]$Difficulties = "",
    [string]$NextSteps = "",
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"

# Cấu hình đường dẫn
$BrainDir = ".\.brain"
$LogDir = "$BrainDir\LOG\phases"
$TasksFile = "$BrainDir\ACTIVE_TASKS.json"
$PhaseFile = "$LogDir\PHASE-$($PhaseNumber.PadLeft(2,'0')).md"

function Get-GitChanges {
    """Lấy danh sách file thay đổi từ git"""
    try {
        $changes = git diff --name-only HEAD~1 2>$null
        if ($changes) {
            return $changes -split "`n" | Where-Object { $_ -ne "" }
        }
    }
    catch {}
    
    # Fallback: lấy file modified trong 1 giờ gần đây
    $recentFiles = Get-ChildItem -Recurse -File | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) -and $_.Name -notmatch "\.log$|\.tmp$" } |
    ForEach-Object { $_.FullName.Substring((Get-Location).Path.Length + 1) }
    
    return $recentFiles
}

function Get-TaskStats {
    """Tính toán thống kê task từ ACTIVE_TASKS.json"""
    if (-not (Test-Path $TasksFile)) {
        return @{
            total       = 0
            completed   = 0
            in_progress = 0
            pending     = 0
            blocked     = 0
            percentage  = 0
        }
    }
    
    try {
        $tasks = Get-Content $TasksFile | ConvertFrom-Json
        $allTasks = $tasks.phases | ForEach-Object { $_.tasks } | ForEach-Object { $_ }
        
        $stats = @{
            total       = $allTasks.Count
            completed   = ($allTasks | Where-Object { $_.status -eq "completed" }).Count
            in_progress = ($allTasks | Where-Object { $_.status -eq "in_progress" }).Count
            pending     = ($allTasks | Where-Object { $_.status -eq "pending" }).Count
            blocked     = ($allTasks | Where-Object { $_.status -eq "blocked" }).Count
        }
        
        if ($stats.total -gt 0) {
            $stats.percentage = [math]::Round(($stats.completed / $stats.total) * 100, 1)
        }
        else {
            $stats.percentage = 0
        }
        
        return $stats
    }
    catch {
        Write-Warning "Error reading tasks file: $($_.Exception.Message)"
        return @{ total = 0; completed = 0; in_progress = 0; pending = 0; blocked = 0; percentage = 0 }
    }
}

function Backup-TasksFile {
    """Backup ACTIVE_TASKS.json"""
    if (Test-Path $TasksFile) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $backupFile = "$LogDir\ACTIVE_TASKS_backup_$timestamp.json"
        Copy-Item $TasksFile $backupFile
        Write-Host "✅ Backed up tasks to: $backupFile" -ForegroundColor Green
    }
}

function Get-InteractiveInput {
    """Thu thập thông tin interactive từ user"""
    Write-Host "📝 Interactive Phase Log Creation" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not $Description) {
        $script:Description = Read-Host "Mô tả phase (Enter để bỏ qua)"
    }
    
    if (-not $StartDate) {
        $defaultStart = (Get-Date).AddHours(-4).ToString("yyyy-MM-dd HH:mm")
        $inputStart = Read-Host "Thời gian bắt đầu [$defaultStart]"
        $script:StartDate = if ($inputStart) { $inputStart } else { $defaultStart }
    }
    
    if (-not $EndDate) {
        $defaultEnd = (Get-Date).ToString("yyyy-MM-dd HH:mm")
        $inputEnd = Read-Host "Thời gian kết thúc [$defaultEnd]"
        $script:EndDate = if ($inputEnd) { $inputEnd } else { $defaultEnd }
    }
    
    if (-not $Difficulties) {
        $script:Difficulties = Read-Host "Khó khăn gặp phải (Enter để bỏ qua)"
    }
    
    if (-not $NextSteps) {
        $script:NextSteps = Read-Host "Gợi ý bước tiếp theo (Enter để bỏ qua)"
    }
    
    # Hiển thị file changes để xác nhận
    Write-Host ""
    Write-Host "📁 File changes detected:" -ForegroundColor Yellow
    $detectedFiles = Get-GitChanges
    if ($detectedFiles) {
        $detectedFiles | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
        $confirmFiles = Read-Host "Sử dụng danh sách file này? (Y/n)"
        if ($confirmFiles -ne "n" -and $confirmFiles -ne "N") {
            $script:FilesChanged = $detectedFiles
        }
    }
    
    if (-not $FilesChanged) {
        Write-Host "Nhập danh sách file thay đổi (mỗi file 1 dòng, Enter trống để kết thúc):"
        $fileList = @()
        do {
            $file = Read-Host "File"
            if ($file) { $fileList += $file }
        } while ($file)
        $script:FilesChanged = $fileList
    }
}

function Create-PhaseLog {
    """Tạo file log phase"""
    
    # Tạo thư mục nếu chưa có
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    
    # Backup tasks file
    Backup-TasksFile
    
    # Lấy thống kê tasks
    $taskStats = Get-TaskStats
    
    # Chuẩn bị nội dung
    $content = @"
# PHASE-$($PhaseNumber.PadLeft(2,'0')): $PhaseName

## ⏰ Thời gian
- **Bắt đầu:** $($StartDate ? $StartDate : (Get-Date).AddHours(-2).ToString("yyyy-MM-dd HH:mm"))
- **Kết thúc:** $($EndDate ? $EndDate : (Get-Date).ToString("yyyy-MM-dd HH:mm"))
- **Tạo log:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## 🎯 Mục tiêu
$($Description ? $Description : "Phát triển và hoàn thiện tính năng $PhaseName")

## 📊 Kết quả

### Files đã tạo/sửa:
"@

    if ($FilesChanged -and $FilesChanged.Count -gt 0) {
        $FilesChanged | ForEach-Object {
            $content += "`n- ``$_``"
        }
    }
    else {
        $content += "`n- *(Không có file nào được ghi nhận)*"
    }

    $content += @"


### Tasks được cập nhật:
"@

    if ($TasksUpdated -and $TasksUpdated.Count -gt 0) {
        $TasksUpdated | ForEach-Object {
            $content += "`n- $_"
        }
    }
    else {
        $content += "`n- *(Sẽ cập nhật thủ công)*"
    }

    $content += @"


### 📈 Thống kê tiến độ:
- **Tổng số task:** $($taskStats.total)
- **Hoàn thành:** $($taskStats.completed)/$($taskStats.total)
- **Đang thực hiện:** $($taskStats.in_progress)
- **Chờ xử lý:** $($taskStats.pending)
- **Bị chặn:** $($taskStats.blocked)
- **Tỷ lệ hoàn thành:** $($taskStats.percentage)%

## 🚫 Khó khăn
$($Difficulties ? $Difficulties : "Không có khó khăn đáng kể")

## 💡 Gợi ý tiếp theo
$($NextSteps ? $NextSteps : "Tiếp tục sang Phase " + ([int]$PhaseNumber + 1).ToString().PadLeft(2,'0') + ": Tối ưu hóa và kiểm thử")

## 🔧 Technical Notes
- **Git commit:** $(try { git rev-parse --short HEAD 2>$null } catch { "N/A" })
- **Branch:** $(try { git branch --show-current 2>$null } catch { "N/A" })
- **Environment:** Windows PowerShell
- **Log generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

---
*Log này được tạo tự động bởi log-phase.ps1*
"@

    # Ghi file
    Set-Content -Path $PhaseFile -Value $content -Encoding UTF8
    
    Write-Host ""
    Write-Host "✅ Phase log created successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $PhaseFile" -ForegroundColor White
    Write-Host ""
    
    # Hiển thị summary
    Write-Host "📊 Phase Summary:" -ForegroundColor Cyan
    Write-Host "   Phase: PHASE-$($PhaseNumber.PadLeft(2,'0')) - $PhaseName" -ForegroundColor White
    Write-Host "   Files changed: $($FilesChanged.Count)" -ForegroundColor White
    Write-Host "   Progress: $($taskStats.completed)/$($taskStats.total) tasks ($($taskStats.percentage)%)" -ForegroundColor White
    Write-Host ""
}

# Main execution
try {
    Write-Host "🚀 Phase Log Generator" -ForegroundColor Green
    Write-Host "=====================" -ForegroundColor Green
    Write-Host ""
    
    # Validate inputs
    if (-not $PhaseNumber -match "^\d+$") {
        throw "Phase number must be numeric"
    }
    
    if (-not $PhaseName) {
        throw "Phase name is required"
    }
    
    # Interactive mode
    if ($Interactive) {
        Get-InteractiveInput
    }
    else {
        # Auto-detect file changes if not provided
        if (-not $FilesChanged -or $FilesChanged.Count -eq 0) {
            Write-Host "🔍 Auto-detecting file changes..." -ForegroundColor Yellow
            $FilesChanged = Get-GitChanges
        }
        
        # Set default dates if not provided
        if (-not $StartDate) {
            $StartDate = (Get-Date).AddHours(-2).ToString("yyyy-MM-dd HH:mm")
        }
        if (-not $EndDate) {
            $EndDate = (Get-Date).ToString("yyyy-MM-dd HH:mm")
        }
    }
    
    # Create the log
    Create-PhaseLog
    
    Write-Host "🎉 Phase logging completed successfully!" -ForegroundColor Green
    
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}