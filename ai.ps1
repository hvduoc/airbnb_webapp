# AI Workflow PowerShell Wrapper
# Usage: .\ai.ps1 start | .\ai.ps1 end | .\ai.ps1 status

param(
    [Parameter(Position = 0)]
    [string]$Command,
    
    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

# Ensure we're in the project directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Not in project root directory" -ForegroundColor Red
    exit 1
}

# Build the Python command
$pythonArgs = @("scripts\ai.py", $Command) + $Arguments
$pythonCommand = "python " + ($pythonArgs -join " ")

# Execute the command
try {
    Invoke-Expression $pythonCommand
    $exitCode = $LASTEXITCODE
}
catch {
    Write-Host "❌ Error executing command: $_" -ForegroundColor Red
    exit 1
}

# Handle special post-commands
if ($Command -eq "start" -and $exitCode -eq 0) {
    Write-Host ""
    Write-Host "🎯 AI SESSION STARTED!" -ForegroundColor Green
    Write-Host "💡 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Check active tasks: .\ai.ps1 task list" -ForegroundColor Cyan
    Write-Host "   2. Start coding on priority tasks" -ForegroundColor Cyan  
    Write-Host "   3. End session when done: .\ai.ps1 end" -ForegroundColor Cyan
}

if ($Command -eq "end" -and $exitCode -eq 0) {
    Write-Host ""
    Write-Host "✅ SESSION COMPLETED!" -ForegroundColor Green
    Write-Host "📝 All progress saved to context files" -ForegroundColor Yellow
    Write-Host "🔄 Ready for next AI session" -ForegroundColor Cyan
}

exit $exitCode