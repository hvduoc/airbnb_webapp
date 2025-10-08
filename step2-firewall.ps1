# Step 2: Setup Firewall (Run as Administrator!)

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Please run PowerShell as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell -> Run as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== CONFIGURING WINDOWS FIREWALL ===" -ForegroundColor Green

Write-Host "Creating firewall rules..." -ForegroundColor Yellow

# Allow HTTP/HTTPS
New-NetFirewallRule -DisplayName "Airbnb-HTTP" -Direction Inbound -Port 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Airbnb-HTTPS" -Direction Inbound -Port 443 -Protocol TCP -Action Allow

# Application ports
New-NetFirewallRule -DisplayName "Airbnb-Webhook" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow  
New-NetFirewallRule -DisplayName "Airbnb-Brain" -Direction Inbound -Port 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Airbnb-API" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow

Write-Host "✅ Firewall rules created" -ForegroundColor Green

# Exclude from Windows Defender
Write-Host "Configuring Windows Defender exclusions..." -ForegroundColor Yellow
Add-MpPreference -ExclusionPath "D:\DUAN1\Airbnb\airbnb_webapp"
Add-MpPreference -ExclusionProcess "python.exe"
Add-MpPreference -ExclusionProcess "node.exe"  
Add-MpPreference -ExclusionProcess "uvicorn.exe"

Write-Host "✅ Windows Defender configured" -ForegroundColor Green
Write-Host "`nNext: Run .\step3-nginx.ps1" -ForegroundColor Cyan