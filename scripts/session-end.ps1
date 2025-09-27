# 📝 SESSION END SCRIPT  
# Purpose: Wrap up development session với proper logging và cleanup

param(
    [string]$Summary = "",
    [switch]$SkipGitCheck = $false,
    [switch]$NoCommit = $false
)

Write-Host "📝 AIRBNB WEBAPP - SESSION END" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
$ProjectRoot = "D:\DUAN1\Airbnb\airbnb_webapp"
Set-Location $ProjectRoot

# Update today's daily log
$Today = Get-Date -Format "yyyy-MM-dd"
$DailyLogPath = ".brain\LOG\daily\$Today.md"

Write-Host "📝 UPDATING DAILY LOG..." -ForegroundColor Yellow

if (Test-Path $DailyLogPath) {
    Write-Host "✅ Daily log found: $DailyLogPath" -ForegroundColor Green
    
    # Add session end timestamp
    $EndTime = Get-Date -Format "HH:mm"
    $SessionEndNote = "`n*End of session: $EndTime*`n*Status: READY for continued development*"
    
    Add-Content -Path $DailyLogPath -Value $SessionEndNote -Encoding UTF8
    Write-Host "✅ Session end time logged" -ForegroundColor Green
    
    if ($Summary -ne "") {
        $SummaryNote = "`n## 📋 SESSION SUMMARY`n$Summary`n"
        Add-Content -Path $DailyLogPath -Value $SummaryNote -Encoding UTF8
        Write-Host "✅ Session summary added" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Daily log not found - creating basic end log" -ForegroundColor Yellow
    
    $BasicLog = @"
# 📅 DAILY LOG - $(Get-Date -Format "MMMM dd, yyyy")

## 📋 SESSION SUMMARY  
Session ended at $(Get-Date -Format "HH:mm") without detailed logging.

*Next session: Review what was accomplished và update this log.*
"@
    
    New-Item -ItemType Directory -Path ".brain\LOG\daily" -Force | Out-Null
    $BasicLog | Out-File -FilePath $DailyLogPath -Encoding UTF8
    Write-Host "✅ Basic end log created" -ForegroundColor Green
}

# Git status và commit check
if (-not $SkipGitCheck) {
    Write-Host ""
    Write-Host "📊 GIT STATUS & COMMIT CHECK..." -ForegroundColor Yellow
    
    try {
        $gitStatus = git status --porcelain 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($gitStatus) {
                Write-Host "📋 Uncommitted changes found:" -ForegroundColor Cyan
                git status --short
                
                Write-Host ""
                Write-Host "🤔 Modified files breakdown:" -ForegroundColor Cyan
                
                # Categorize changes
                $BrainFiles = @()
                $CodeFiles = @()
                $OtherFiles = @()
                
                foreach ($line in $gitStatus) {
                    $file = $line.Substring(3)
                    if ($file -like ".brain/*") {
                        $BrainFiles += $file
                    } elseif ($file -like "*.py" -or $file -like "*.html" -or $file -like "*.js") {
                        $CodeFiles += $file  
                    } else {
                        $OtherFiles += $file
                    }
                }
                
                if ($BrainFiles.Count -gt 0) {
                    Write-Host "   🧠 Brain files: $($BrainFiles.Count)" -ForegroundColor Blue
                    $BrainFiles | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
                }
                
                if ($CodeFiles.Count -gt 0) {
                    Write-Host "   💻 Code files: $($CodeFiles.Count)" -ForegroundColor Green  
                    $CodeFiles | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
                }
                
                if ($OtherFiles.Count -gt 0) {
                    Write-Host "   📄 Other files: $($OtherFiles.Count)" -ForegroundColor Yellow
                    $OtherFiles | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
                }
                
                if (-not $NoCommit) {
                    Write-Host ""
                    $commitChoice = Read-Host "💾 Commit these changes? (y/N)"
                    
                    if ($commitChoice -eq "y" -or $commitChoice -eq "Y") {
                        Write-Host "📝 Staging all changes..." -ForegroundColor Yellow
                        git add .
                        
                        if ($Summary -ne "") {
                            $commitMessage = "feat: $Summary"
                        } else {
                            $defaultMessage = "feat: Session end - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
                            $customMessage = Read-Host "💬 Commit message (Enter for default: '$defaultMessage')"
                            $commitMessage = if ($customMessage) { $customMessage } else { $defaultMessage }
                        }
                        
                        Write-Host "💾 Committing với message: $commitMessage" -ForegroundColor Green
                        git commit -m $commitMessage
                        
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "✅ Changes committed successfully" -ForegroundColor Green
                        } else {
                            Write-Host "❌ Commit failed" -ForegroundColor Red
                        }
                    } else {
                        Write-Host "ℹ️  Changes left uncommitted" -ForegroundColor Gray
                    }
                }
                
            } else {
                Write-Host "✅ Working directory clean - no uncommitted changes" -ForegroundColor Green
            }
        } else {
            Write-Host "ℹ️  Not a git repository or git not available" -ForegroundColor Gray
        }
    } catch {
        Write-Host "ℹ️  Git check skipped due to error: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

# Brain system health check
Write-Host ""
Write-Host "🧠 BRAIN SYSTEM FINAL CHECK..." -ForegroundColor Yellow

$RequiredFiles = @(
    ".brain\README.md",
    ".brain\CONTEXT_INDEX.md",
    ".brain\SCOPE.md", 
    ".brain\ACTIVE_TASKS.json",
    ".brain\PLAYBOOKS\COPILOT_GUARDRAILS.md"
)

$HealthyFiles = 0
foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        $HealthyFiles++
    }
}

$HealthPercent = [math]::Round(($HealthyFiles / $RequiredFiles.Count) * 100)

if ($HealthPercent -eq 100) {
    Write-Host "✅ Brain system: HEALTHY ($HealthPercent%)" -ForegroundColor Green
} elseif ($HealthPercent -ge 80) {
    Write-Host "⚠️  Brain system: MOSTLY HEALTHY ($HealthPercent%)" -ForegroundColor Yellow
} else {
    Write-Host "❌ Brain system: NEEDS ATTENTION ($HealthPercent%)" -ForegroundColor Red
    Write-Host "💡 Run session-start.ps1 to see missing files" -ForegroundColor Cyan
}

# Next session preparation
Write-Host ""
Write-Host "📋 NEXT SESSION PREPARATION..." -ForegroundColor Yellow

# Check active tasks
if (Test-Path ".brain\ACTIVE_TASKS.json") {
    try {
        $Tasks = Get-Content ".brain\ACTIVE_TASKS.json" -Raw | ConvertFrom-Json
        $ReadyTasks = $Tasks | Where-Object { $_.status -eq "ready" }
        
        if ($ReadyTasks.Count -gt 0) {
            Write-Host "✅ $($ReadyTasks.Count) ready tasks available for next session" -ForegroundColor Green
            Write-Host "🎯 Highest priority: $($ReadyTasks[0].id) - $($ReadyTasks[0].title)" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️  No ready tasks found - consider updating ACTIVE_TASKS.json" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Error reading ACTIVE_TASKS.json - may need validation" -ForegroundColor Red
    }
}

# Environment cleanup suggestions
Write-Host ""
Write-Host "🧹 CLEANUP SUGGESTIONS..." -ForegroundColor Yellow

# Check for running processes
$AppRunning = Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue
if ($AppRunning) {
    Write-Host "🔄 FastAPI app still running (PID: $($AppRunning.Id))" -ForegroundColor Blue
    $stopChoice = Read-Host "🛑 Stop the app? (y/N)"
    if ($stopChoice -eq "y" -or $stopChoice -eq "Y") {
        Stop-Process -Id $AppRunning.Id -Force
        Write-Host "✅ App stopped" -ForegroundColor Green
    }
} else {
    Write-Host "✅ No running app processes detected" -ForegroundColor Green
}

# Final summary
Write-Host ""
Write-Host "🎉 SESSION END COMPLETE" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Session Statistics:" -ForegroundColor Cyan
Write-Host "   • Daily log: Updated với session end" -ForegroundColor White
Write-Host "   • Brain health: $HealthPercent%" -ForegroundColor White
Write-Host "   • Git status: $(if ($gitStatus) { 'Changes detected' } else { 'Clean' })" -ForegroundColor White
Write-Host ""

if ($Summary -ne "") {
    Write-Host "📝 Session Summary: $Summary" -ForegroundColor Green
}

Write-Host "💤 Ready for next development session!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next session: Run .\scripts\session-start.ps1" -ForegroundColor Cyan
Write-Host ""

# Usage examples
Write-Host "💡 Usage Examples:" -ForegroundColor Yellow
Write-Host "   .\scripts\session-end.ps1                                    # Basic session end" -ForegroundColor Gray
Write-Host "   .\scripts\session-end.ps1 -Summary 'Completed room tracking' # With summary" -ForegroundColor Gray
Write-Host "   .\scripts\session-end.ps1 -NoCommit                          # Skip commit prompt" -ForegroundColor Gray
Write-Host "   .\scripts\session-end.ps1 -SkipGitCheck                      # Skip git operations" -ForegroundColor Gray