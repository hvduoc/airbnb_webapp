# PowerShell Script để đồng bộ .brain/ files từ GitHub
# sync-brain-files.ps1

param(
    [string]$RepoUrl = "https://github.com/your-org/airbnb-webapp.git",
    [string]$TempDir = ".\temp_sync",
    [string]$BrainDest = ".\brain-ui\public\brain",
    [switch]$Verbose
)

# Cấu hình
$ErrorActionPreference = "Stop"
$LogFile = "sync-brain-log.txt"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    Write-Host $LogEntry -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
    )
    
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-GitInstalled {
    try {
        $null = git --version
        return $true
    }
    catch {
        return $false
    }
}

function Sync-Repository {
    Write-Log "Starting Brain data sync from $RepoUrl"
    
    # Kiểm tra Git
    if (-not (Test-GitInstalled)) {
        throw "Git is not installed or not in PATH"
    }
    
    # Clone hoặc pull repository
    if (Test-Path $TempDir) {
        Write-Log "Temp directory exists, pulling latest changes"
        try {
            Set-Location $TempDir
            git pull origin main
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Git pull failed, removing and cloning fresh" "WARN"
                Set-Location ..
                Remove-Item -Recurse -Force $TempDir
                git clone $RepoUrl $TempDir
            }
        }
        finally {
            Set-Location $PSScriptRoot
        }
    }
    else {
        Write-Log "Cloning repository"
        git clone $RepoUrl $TempDir
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to clone/pull repository"
    }
    
    # Kiểm tra .brain directory tồn tại
    $BrainSource = Join-Path $TempDir ".brain"
    if (-not (Test-Path $BrainSource)) {
        throw ".brain directory not found in repository"
    }
    
    # Tạo destination directory
    if (-not (Test-Path $BrainDest)) {
        New-Item -ItemType Directory -Path $BrainDest -Force | Out-Null
    }
    
    # Copy files
    Write-Log "Copying .brain files to $BrainDest"
    
    $FilesCount = 0
    Get-ChildItem -Path $BrainSource -Recurse -File | ForEach-Object {
        $RelativePath = $_.FullName.Substring($BrainSource.Length + 1)
        $DestFile = Join-Path $BrainDest $RelativePath
        $DestDir = Split-Path $DestFile -Parent
        
        if (-not (Test-Path $DestDir)) {
            New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
        }
        
        Copy-Item -Path $_.FullName -Destination $DestFile -Force
        if ($Verbose) {
            Write-Log "Copied: $RelativePath"
        }
        $FilesCount++
    }
    
    Write-Log "Successfully synced $FilesCount files" "SUCCESS"
    
    # Cleanup temp directory (tùy chọn)
    # Remove-Item -Recurse -Force $TempDir
    
    return @{
        Success    = $true
        FilesCount = $FilesCount
        Timestamp  = Get-Date
    }
}

# Main execution
try {
    $Result = Sync-Repository
    
    Write-Log "=== SYNC COMPLETED SUCCESSFULLY ===" "SUCCESS"
    Write-Log "Files synced: $($Result.FilesCount)" "SUCCESS"
    Write-Log "Timestamp: $($Result.Timestamp)" "SUCCESS"
    
    exit 0
}
catch {
    Write-Log "=== SYNC FAILED ===" "ERROR"
    Write-Log $_.Exception.Message "ERROR"
    
    exit 1
}