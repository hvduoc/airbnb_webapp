# CREATE BRAIN FROM TEMPLATE - PowerShell Script
# Muc tieu: Setup brain system tu template trong < 5 phut

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,
    [Parameter(Mandatory=$false)]
    [string]$Team = "Development Team",
    [Parameter(Mandatory=$false)]
    [string]$Domain = "SaaS",
    [Parameter(Mandatory=$false)]
    [string]$TargetPath = ".brain"
)

Write-Host "SETUP BRAIN SYSTEM CHO DU AN: $ProjectName" -ForegroundColor Green
$startTime = Get-Date

# Kiem tra PROJECT_TEMPLATE ton tai
$templatePath = ".brain/PROJECT_TEMPLATE"
if (-not (Test-Path $templatePath)) {
    $templatePath = "."  # Neu chay tu trong thu muc template
}

Write-Host "Tim thay template directory: $templatePath" -ForegroundColor Green

# Tao thu muc dich neu chua ton tai
if (-not (Test-Path $TargetPath)) {
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
}

# Tao thu muc con
$subDirs = @("tasks", "context", "logs/daily")
foreach ($dir in $subDirs) {
    $fullPath = Join-Path $TargetPath $dir
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
}

# Copy va rename template files
$templateFiles = @{
    "TEMPLATE_SCOPE.md" = "SCOPE.md"
    "TEMPLATE_DOMAIN_MAP.md" = "DOMAIN_MAP.md" 
    "SAMPLE_ACTIVE_TASKS.json" = "tasks/ACTIVE_TASKS.json"
    "QUICK_START.md" = "QUICK_START.md"
}

Write-Host "Dang copy template files..." -ForegroundColor Yellow

foreach ($sourceFile in $templateFiles.Keys) {
    $sourcePath = Join-Path $templatePath $sourceFile
    $destFile = $templateFiles[$sourceFile] 
    $destPath = Join-Path $TargetPath $destFile
    
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $destPath -Force
        Write-Host "Copied: $sourceFile -> $destFile" -ForegroundColor Green
    }
}

# Thay the placeholders
$currentDate = Get-Date -Format "yyyy-MM-dd"
$placeholders = @{
    "{{PROJECT_NAME}}" = $ProjectName
    "{{TEAM_NAME}}" = $Team
    "{{DOMAIN}}" = $Domain
    "{{CURRENT_DATE}}" = $currentDate
    "{{LAST_UPDATED}}" = $currentDate
    "{{VERSION}}" = "1.0.0"
    "{{STATUS}}" = "Development"
}

Write-Host "Dang thay the placeholders..." -ForegroundColor Yellow

# Thay trong SCOPE.md
$scopePath = Join-Path $TargetPath "SCOPE.md"
if (Test-Path $scopePath) {
    $content = Get-Content $scopePath -Raw
    foreach ($placeholder in $placeholders.Keys) {
        $replacement = $placeholders[$placeholder]
        $content = $content -replace [regex]::Escape($placeholder), $replacement
    }
    Set-Content $scopePath $content
    Write-Host "Updated: SCOPE.md" -ForegroundColor Green
}

# Tao JSON don gian
$jsonPath = Join-Path $TargetPath "tasks/ACTIVE_TASKS.json"
$jsonContent = @"
{
  "project": {
    "name": "$ProjectName",
    "version": "1.0.0",
    "domain": "$Domain",
    "status": "Development",
    "last_updated": "$currentDate"
  },
  "active_tasks": [
    {
      "id": "SETUP-001",
      "title": "Project Setup Complete",
      "status": "Done",
      "priority": "High",
      "progress": "100%"
    }
  ],
  "metrics": {
    "total_tasks": 1,
    "completed_tasks": 1
  }
}
"@

Set-Content $jsonPath $jsonContent
Write-Host "Created: ACTIVE_TASKS.json" -ForegroundColor Green

# Tinh thoi gian
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "HOAN THANH SETUP!" -ForegroundColor Green
Write-Host "Thoi gian setup: $([math]::Round($duration, 1)) giay" -ForegroundColor Cyan
Write-Host "Brain system da san sang cho du an $ProjectName!" -ForegroundColor Green