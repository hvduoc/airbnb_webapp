# 🚀 SESSION START SCRIPT
# Purpose: Initialize daily development session với complete brain context loading

param(
    [string]$TaskId = "",
    [switch]$SkipGitCheck = $false
)

Write-Host "🧠 AIRBNB WEBAPP - SESSION START" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
$ProjectRoot = "D:\DUAN1\Airbnb\airbnb_webapp"
Set-Location $ProjectRoot

Write-Host "📂 Working Directory: $ProjectRoot" -ForegroundColor Green

# Check if .brain system is complete
Write-Host ""
Write-Host "🔍 BRAIN SYSTEM HEALTH CHECK..." -ForegroundColor Yellow

$RequiredFiles = @(
    ".brain\README.md",
    ".brain\CONTEXT_INDEX.md", 
    ".brain\SCOPE.md",
    ".brain\ACTIVE_TASKS.json",
    ".brain\DOMAIN_MAP.md",
    ".brain\GLOSSARY.md",
    ".brain\RISKS.md",
    ".brain\METRICS.md",
    ".brain\PLAYBOOKS\COPILOT_GUARDRAILS.md"
)

$MissingFiles = @()
foreach ($file in $RequiredFiles) {
    if (-not (Test-Path $file)) {
        $MissingFiles += $file
    }
    else {
        Write-Host "✅ $file" -ForegroundColor Green
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ MISSING BRAIN FILES:" -ForegroundColor Red
    foreach ($file in $MissingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "🚨 Cannot start session without complete brain context!" -ForegroundColor Red
    Write-Host "📖 Run brain setup script first or check .brain/README.md" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎉 Brain system health: OK" -ForegroundColor Green

# Create today's daily log if not exists
$Today = Get-Date -Format "yyyy-MM-dd"
$DailyLogPath = ".brain\LOG\daily\$Today.md"

if (-not (Test-Path $DailyLogPath)) {
    Write-Host ""
    Write-Host "📝 Creating daily log: $DailyLogPath" -ForegroundColor Yellow
    
    $LogTemplate = @'
# Daily LOG - {0}

Session Focus: Describe today's main objectives

---

## TODAY'S OBJECTIVES  
* Add specific tasks for today
* Reference ACTIVE_TASKS.json for context

## COMPLETED TASKS

### [Time] Task Description
* Task: What was done
* Outcome: Results achieved  
* Files Modified: List files changed
* Next Action: What's next

## METRICS & PROGRESS
* Development Time: Hours spent
* Tasks Completed: Count/List
* Quality Indicators: Code quality, tests, docs

## ISSUES & BLOCKERS
* I01: Issue description - Priority: High/Medium/Low - Status: Active/Resolved

## TOMORROW'S PRIORITIES
1. Next task
2. Following task

Session start: {1}
'@ -f (Get-Date -Format "MMMM dd, yyyy"), (Get-Date -Format "HH:mm")

    $LogTemplate | Out-File -FilePath $DailyLogPath -Encoding UTF8
    Write-Host "✅ Daily log created" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "📝 Using existing daily log: $DailyLogPath" -ForegroundColor Green
}

# Display active tasks
Write-Host ""
Write-Host "🎯 ACTIVE TASKS SUMMARY..." -ForegroundColor Yellow

if (Test-Path ".brain\ACTIVE_TASKS.json") {
    try {
        $Tasks = Get-Content ".brain\ACTIVE_TASKS.json" -Raw | ConvertFrom-Json
        
        Write-Host ""
        Write-Host "📋 Available Tasks:" -ForegroundColor Cyan
        foreach ($task in $Tasks) {
            $status = if ($task.status -eq "ready") { "🟢" } elseif ($task.status -eq "in_progress") { "🟡" } else { "🔴" }
            Write-Host "   $status $($task.id): $($task.title)" -ForegroundColor White
            Write-Host "      Priority: $($task.priority) | Estimated: $($task.estimated_hours)" -ForegroundColor Gray
        }
        
        if ($TaskId -ne "") {
            $selectedTask = $Tasks | Where-Object { $_.id -eq $TaskId }
            if ($selectedTask) {
                Write-Host ""
                Write-Host "🎯 SELECTED TASK: $TaskId" -ForegroundColor Green
                Write-Host "   Title: $($selectedTask.title)" -ForegroundColor White
                Write-Host "   Scope: $($selectedTask.scope -join ', ')" -ForegroundColor Gray
                Write-Host "   Files: $($selectedTask.files -join ', ')" -ForegroundColor Gray
            }
            else {
                Write-Host ""
                Write-Host "❌ Task ID '$TaskId' not found in ACTIVE_TASKS.json" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "❌ Error reading ACTIVE_TASKS.json: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "❌ ACTIVE_TASKS.json not found" -ForegroundColor Red
}

# Git status check (if not skipped)
if (-not $SkipGitCheck) {
    Write-Host ""
    Write-Host "📊 GIT STATUS CHECK..." -ForegroundColor Yellow
    
    try {
        $gitStatus = git status --porcelain 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($gitStatus) {
                Write-Host "⚠️  Uncommitted changes found:" -ForegroundColor Yellow
                git status --short
                Write-Host ""
                Write-Host "💡 Consider committing changes before starting new work" -ForegroundColor Cyan
            }
            else {
                Write-Host "✅ Working directory clean" -ForegroundColor Green
            }
        }
        else {
            Write-Host "ℹ️  Not a git repository or git not available" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "ℹ️  Git status check skipped" -ForegroundColor Gray
    }
}

# Environment check
Write-Host ""
Write-Host "🔧 ENVIRONMENT CHECK..." -ForegroundColor Yellow

# Check Python environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Python virtual environment found" -ForegroundColor Green
    Write-Host "💡 Activate with: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
}
else {
    Write-Host "⚠️  Python virtual environment not found" -ForegroundColor Yellow
    Write-Host "💡 Create with: python -m venv venv" -ForegroundColor Cyan
}

# Check if app is running
$AppRunning = Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue
if ($AppRunning) {
    Write-Host "✅ FastAPI app appears to be running" -ForegroundColor Green
}
else {
    Write-Host "ℹ️  FastAPI app not detected running" -ForegroundColor Gray
    Write-Host "💡 Start with: uvicorn main:app --reload" -ForegroundColor Cyan
}

# Session summary
Write-Host ""
Write-Host "🎉 SESSION INITIALIZED SUCCESSFULLY" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Quick Reference:" -ForegroundColor Cyan
Write-Host "   • Daily log: $DailyLogPath" -ForegroundColor White
Write-Host "   • Brain files: .brain\CONTEXT_INDEX.md" -ForegroundColor White
Write-Host "   • Active tasks: .brain\ACTIVE_TASKS.json" -ForegroundColor White
Write-Host "   • Guardrails: .brain\PLAYBOOKS\COPILOT_GUARDRAILS.md" -ForegroundColor White
Write-Host ""
Write-Host "🤖 AI Agents: Use updated .prompts\01_SESSION_START.md" -ForegroundColor Cyan
Write-Host ""

# Usage examples
Write-Host "💡 Usage Examples:" -ForegroundColor Yellow
Write-Host "   .\scripts\session-start.ps1                    # General session start" -ForegroundColor Gray  
Write-Host "   .\scripts\session-start.ps1 -TaskId TASK-001   # Focus on specific task" -ForegroundColor Gray
Write-Host "   .\scripts\session-start.ps1 -SkipGitCheck      # Skip git status check" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 Ready to code! Happy development session! 🎯" -ForegroundColor Green