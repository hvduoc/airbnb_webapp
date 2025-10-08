# PowerShell Script để cập nhật trạng thái task
# update-task-status.ps1

param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,
    
    [Parameter(Mandatory = $true)]
    [ValidateSet("pending", "in_progress", "completed", "blocked", "cancelled")]
    [string]$NewStatus,
    
    [string]$Comment = "",
    [switch]$Interactive,
    [switch]$ListTasks
)

$ErrorActionPreference = "Stop"

# Cấu hình
$TasksFile = ".\.brain\ACTIVE_TASKS.json"
$BackupDir = ".\.brain\LOG"

function Show-TaskList {
    """Hiển thị danh sách tất cả tasks"""
    if (-not (Test-Path $TasksFile)) {
        Write-Host "❌ Tasks file not found: $TasksFile" -ForegroundColor Red
        return
    }
    
    try {
        $tasks = Get-Content $TasksFile | ConvertFrom-Json
        
        Write-Host "📋 All Available Tasks:" -ForegroundColor Cyan
        Write-Host "======================" -ForegroundColor Cyan
        Write-Host ""
        
        $allTasks = @()
        foreach ($phase in $tasks.phases) {
            foreach ($task in $phase.tasks) {
                $allTasks += [PSCustomObject]@{
                    Phase    = $phase.phase_name
                    Id       = $task.id
                    Title    = $task.title
                    Status   = $task.status
                    Priority = $task.priority
                    Assignee = $task.assignee
                    Progress = "$($task.progress)%"
                }
            }
        }
        
        $allTasks | Format-Table -AutoSize
        
        # Thống kê
        $stats = $allTasks | Group-Object Status | Sort-Object Name
        Write-Host "📊 Status Summary:" -ForegroundColor Yellow
        $stats | ForEach-Object {
            $color = switch ($_.Name) {
                "completed" { "Green" }
                "in_progress" { "Yellow" }
                "blocked" { "Red" }
                "cancelled" { "DarkRed" }
                default { "White" }
            }
            Write-Host "   $($_.Name): $($_.Count)" -ForegroundColor $color
        }
        
    }
    catch {
        Write-Host "❌ Error reading tasks: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Backup-TasksFile {
    """Backup tasks file trước khi thay đổi"""
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupFile = "$BackupDir\ACTIVE_TASKS_backup_$timestamp.json"
    Copy-Item $TasksFile $backupFile
    
    Write-Host "✅ Backed up tasks to: $backupFile" -ForegroundColor Green
}

function Find-Task {
    param([string]$Id, [object]$TasksData)
    
    foreach ($phase in $TasksData.phases) {
        foreach ($task in $phase.tasks) {
            if ($task.id -eq $Id) {
                return @{
                    Phase      = $phase
                    Task       = $task
                    PhaseIndex = [array]::IndexOf($TasksData.phases, $phase)
                    TaskIndex  = [array]::IndexOf($phase.tasks, $task)
                }
            }
        }
    }
    return $null
}

function Update-TaskStatus {
    """Cập nhật trạng thái task"""
    
    if (-not (Test-Path $TasksFile)) {
        Write-Host "❌ Tasks file not found: $TasksFile" -ForegroundColor Red
        return $false
    }
    
    try {
        # Backup trước khi thay đổi
        Backup-TasksFile
        
        # Đọc tasks
        $tasksData = Get-Content $TasksFile | ConvertFrom-Json
        
        # Tìm task cần update
        $taskInfo = Find-Task -Id $TaskId -TasksData $tasksData
        
        if (-not $taskInfo) {
            Write-Host "❌ Task with ID '$TaskId' not found" -ForegroundColor Red
            Write-Host "💡 Use -ListTasks to see all available tasks" -ForegroundColor Yellow
            return $false
        }
        
        $task = $taskInfo.Task
        $oldStatus = $task.status
        
        # Hiển thị thông tin task hiện tại
        Write-Host ""
        Write-Host "📝 Task Information:" -ForegroundColor Cyan
        Write-Host "   ID: $($task.id)" -ForegroundColor White
        Write-Host "   Title: $($task.title)" -ForegroundColor White
        Write-Host "   Current Status: $oldStatus" -ForegroundColor Yellow
        Write-Host "   New Status: $NewStatus" -ForegroundColor Green
        Write-Host "   Phase: $($taskInfo.Phase.phase_name)" -ForegroundColor Gray
        Write-Host ""
        
        # Xác nhận thay đổi trong interactive mode
        if ($Interactive) {
            $confirm = Read-Host "Confirm update? (Y/n)"
            if ($confirm -eq "n" -or $confirm -eq "N") {
                Write-Host "❌ Update cancelled" -ForegroundColor Yellow
                return $false
            }
        }
        
        # Cập nhật task
        $task.status = $NewStatus
        $task.updated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        
        # Cập nhật progress dựa trên status
        switch ($NewStatus) {
            "pending" { $task.progress = 0 }
            "in_progress" { 
                if ($task.progress -eq 0) { $task.progress = 25 }
            }
            "completed" { $task.progress = 100 }
            "blocked" { 
                # Giữ nguyên progress
            }
            "cancelled" { $task.progress = 0 }
        }
        
        # Thêm comment nếu có
        if ($Comment) {
            if (-not $task.comments) {
                $task | Add-Member -MemberType NoteProperty -Name "comments" -Value @()
            }
            
            $newComment = [PSCustomObject]@{
                timestamp     = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
                comment       = $Comment
                status_change = "$oldStatus → $NewStatus"
            }
            
            $task.comments += $newComment
        }
        
        # Lưu file
        $tasksData | ConvertTo-Json -Depth 10 | Set-Content $TasksFile -Encoding UTF8
        
        Write-Host "✅ Task updated successfully!" -ForegroundColor Green
        Write-Host "   $($task.id): $oldStatus → $NewStatus" -ForegroundColor White
        
        if ($Comment) {
            Write-Host "   Comment added: $Comment" -ForegroundColor Gray
        }
        
        # Hiển thị thống kê cập nhật
        $stats = @{}
        foreach ($phase in $tasksData.phases) {
            foreach ($t in $phase.tasks) {
                $status = $t.status
                if (-not $stats.ContainsKey($status)) {
                    $stats[$status] = 0
                }
                $stats[$status]++
            }
        }
        
        Write-Host ""
        Write-Host "📊 Updated Statistics:" -ForegroundColor Cyan
        foreach ($status in $stats.Keys | Sort-Object) {
            $color = switch ($status) {
                "completed" { "Green" }
                "in_progress" { "Yellow" }
                "blocked" { "Red" }
                "cancelled" { "DarkRed" }
                default { "White" }
            }
            Write-Host "   $status`: $($stats[$status])" -ForegroundColor $color
        }
        
        return $true
        
    }
    catch {
        Write-Host "❌ Error updating task: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Interactive-TaskUpdate {
    """Interactive mode để chọn task và status"""
    
    Write-Host "🎯 Interactive Task Status Update" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Hiển thị danh sách tasks
    Show-TaskList
    
    # Chọn task
    if (-not $TaskId) {
        $script:TaskId = Read-Host "Enter Task ID to update"
    }
    
    # Chọn status
    if (-not $NewStatus) {
        Write-Host ""
        Write-Host "📝 Available Statuses:" -ForegroundColor Yellow
        Write-Host "   1. pending"
        Write-Host "   2. in_progress"
        Write-Host "   3. completed"
        Write-Host "   4. blocked"
        Write-Host "   5. cancelled"
        Write-Host ""
        
        $statusChoice = Read-Host "Select new status (1-5 or name)"
        
        $script:NewStatus = switch ($statusChoice) {
            "1" { "pending" }
            "2" { "in_progress" }  
            "3" { "completed" }
            "4" { "blocked" }
            "5" { "cancelled" }
            default { $statusChoice }
        }
    }
    
    # Comment
    if (-not $Comment) {
        $script:Comment = Read-Host "Add comment (optional)"
    }
}

# Main execution
try {
    Write-Host "🔄 Task Status Updater" -ForegroundColor Green
    Write-Host "=====================" -ForegroundColor Green
    Write-Host ""
    
    # List tasks mode
    if ($ListTasks) {
        Show-TaskList
        exit 0
    }
    
    # Interactive mode
    if ($Interactive) {
        Interactive-TaskUpdate
    }
    
    # Validate inputs
    if (-not $TaskId) {
        Write-Host "❌ Task ID is required" -ForegroundColor Red
        Write-Host "💡 Use -ListTasks to see available tasks" -ForegroundColor Yellow
        exit 1
    }
    
    if (-not $NewStatus) {
        Write-Host "❌ New status is required" -ForegroundColor Red
        exit 1
    }
    
    # Validate status
    $validStatuses = @("pending", "in_progress", "completed", "blocked", "cancelled")
    if ($NewStatus -notin $validStatuses) {
        Write-Host "❌ Invalid status: $NewStatus" -ForegroundColor Red
        Write-Host "💡 Valid statuses: $($validStatuses -join ', ')" -ForegroundColor Yellow
        exit 1
    }
    
    # Update task
    if (Update-TaskStatus) {
        Write-Host ""
        Write-Host "🎉 Task status updated successfully!" -ForegroundColor Green
    }
    else {
        exit 1
    }
    
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}