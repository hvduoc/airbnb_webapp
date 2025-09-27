# Test Script đơn giản để list tasks
# test-tasks.ps1

$TasksFile = ".\.brain\tasks\ACTIVE_TASKS.json"

if (-not (Test-Path $TasksFile)) {
    Write-Host "Tasks file not found: $TasksFile" -ForegroundColor Red
    exit 1
}

try {
    $tasks = Get-Content $TasksFile | ConvertFrom-Json
    
    Write-Host "All Available Tasks:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($phase in $tasks.phases) {
        Write-Host "Phase: $($phase.phase_name)" -ForegroundColor Yellow
        foreach ($task in $phase.tasks) {
            Write-Host "  ID: $($task.id)" -ForegroundColor White
            Write-Host "  Title: $($task.title)" -ForegroundColor White
            Write-Host "  Status: $($task.status)" -ForegroundColor Green
            Write-Host "  Priority: $($task.priority)" -ForegroundColor Blue
            Write-Host "  Progress: $($task.progress)%" -ForegroundColor Magenta
            Write-Host ""
        }
    }
    
} catch {
    Write-Host "Error reading tasks: $($_.Exception.Message)" -ForegroundColor Red
}