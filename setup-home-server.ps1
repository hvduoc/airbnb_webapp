# 🔧 Quick Setup Script - Home Server

## AUTO SETUP - Chạy từng bước

### STEP 1: Check Environment
```powershell
# Run this first to check your setup
Write-Host "=== CHECKING HOME SERVER ENVIRONMENT ===" -ForegroundColor Green

# Check public IP
Write-Host "Getting public IP..." -ForegroundColor Yellow
try {
    $publicIP = (Invoke-RestMethod -Uri "https://ipapi.co/ip/").Trim()
    Write-Host "✅ Public IP: $publicIP" -ForegroundColor Green
    $publicIP | Out-File -FilePath "public-ip.txt"
}
catch {
    Write-Host "❌ Cannot get public IP. Check internet connection." -ForegroundColor Red
    exit 1
}

# Check local IP  
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq "Dhcp" }).IPAddress | Select-Object -First 1
Write-Host "✅ Local IP: $localIP" -ForegroundColor Green

# Test connection
Write-Host "Testing internet connection..." -ForegroundColor Yellow
$testResult = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet
if ($testResult) {
    Write-Host "✅ Internet connection: OK" -ForegroundColor Green
}
else {
    Write-Host "❌ Internet connection: FAILED" -ForegroundColor Red
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "1. Configure router port forwarding:" -ForegroundColor White
Write-Host "   80 -> $localIP:80" -ForegroundColor Gray
Write-Host "   443 -> $localIP:443" -ForegroundColor Gray  
Write-Host "   8080 -> $localIP:8080" -ForegroundColor Gray
Write-Host "   3000 -> $localIP:3000" -ForegroundColor Gray
Write-Host "   8000 -> $localIP:8000" -ForegroundColor Gray
Write-Host "`n2. Router admin: http://192.168.1.1 (most common)" -ForegroundColor White
Write-Host "3. Run Step 2 after router configuration" -ForegroundColor White
```

### STEP 2: Setup Firewall
```powershell
# Run as Administrator!
Write-Host "=== CONFIGURING WINDOWS FIREWALL ===" -ForegroundColor Green

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Please run PowerShell as Administrator!" -ForegroundColor Red
    exit 1
}

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
Write-Host "`nNext: Run Step 3 to download Nginx" -ForegroundColor Cyan
```

### STEP 3: Setup Nginx
```powershell
Write-Host "=== SETTING UP NGINX ===" -ForegroundColor Green

# Download nginx
$nginxDir = "C:\nginx"
if (Test-Path $nginxDir) {
    Write-Host "Nginx already exists, skipping download..." -ForegroundColor Yellow
}
else {
    Write-Host "Downloading Nginx..." -ForegroundColor Yellow
    $nginxUrl = "http://nginx.org/download/nginx-1.24.0.zip"
    $nginxZip = "$env:TEMP\nginx.zip"
    
    Invoke-WebRequest -Uri $nginxUrl -OutFile $nginxZip
    Expand-Archive -Path $nginxZip -DestinationPath "C:\"
    
    # Rename folder
    if (Test-Path "C:\nginx-1.24.0") {
        Rename-Item "C:\nginx-1.24.0" "nginx"
    }
    
    Write-Host "✅ Nginx downloaded to C:\nginx" -ForegroundColor Green
}

# Get current IP for config
$publicIP = Get-Content "public-ip.txt" -ErrorAction SilentlyContinue
if (-not $publicIP) {
    $publicIP = "YOUR_PUBLIC_IP"
}

# Create nginx.conf
$nginxConf = @"
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    upstream brain_ui {
        server 127.0.0.1:3000;
    }
    
    upstream api_server {
        server 127.0.0.1:8000;
    }
    
    upstream webhook_server {
        server 127.0.0.1:8080;
    }

    # Brain UI
    server {
        listen 80;
        server_name brain.xemgiadat.com $publicIP;
        
        location / {
            proxy_pass http://brain_ui;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        }
    }

    # API Server  
    server {
        listen 80;
        server_name api.xemgiadat.com;
        
        location / {
            proxy_pass http://api_server;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        }
    }

    # Webhook Server
    server {
        listen 80;
        server_name webhook.xemgiadat.com;
        
        location / {
            proxy_pass http://webhook_server;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        }
    }
}
"@

$nginxConf | Out-File -FilePath "C:\nginx\conf\nginx.conf" -Encoding UTF8

Write-Host "✅ Nginx configuration created" -ForegroundColor Green

# Test nginx configuration
Write-Host "Testing nginx configuration..." -ForegroundColor Yellow
$testResult = & "C:\nginx\nginx.exe" -t 2>&1
if ($testResult -like "*successful*") {
    Write-Host "✅ Nginx configuration is valid" -ForegroundColor Green
}
else {
    Write-Host "❌ Nginx configuration error:" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
}

Write-Host "`nNext: Run Step 4 to start services" -ForegroundColor Cyan
```

### STEP 4: Start All Services
```powershell
Write-Host "=== STARTING ALL SERVICES ===" -ForegroundColor Green

# Start nginx
Write-Host "Starting Nginx..." -ForegroundColor Yellow
Start-Process -FilePath "C:\nginx\nginx.exe" -WindowStyle Hidden
Start-Sleep -Seconds 2

# Check if nginx started
$nginxProcess = Get-Process nginx -ErrorAction SilentlyContinue
if ($nginxProcess) {
    Write-Host "✅ Nginx started (PID: $($nginxProcess.Id))" -ForegroundColor Green
}
else {
    Write-Host "❌ Nginx failed to start" -ForegroundColor Red
}

Write-Host "`n=== MANUAL SERVICE START ===" -ForegroundColor Cyan
Write-Host "Open 3 PowerShell terminals and run:" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 1 - Webhook Server:" -ForegroundColor Yellow
Write-Host "cd D:\DUAN1\Airbnb\airbnb_webapp" -ForegroundColor Gray
Write-Host "uvicorn webhook_listener:app --host 0.0.0.0 --port 8080 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "Terminal 2 - API Server:" -ForegroundColor Yellow  
Write-Host "cd D:\DUAN1\Airbnb\airbnb_webapp" -ForegroundColor Gray
Write-Host "uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "Terminal 3 - Brain UI:" -ForegroundColor Yellow
Write-Host "cd D:\DUAN1\Airbnb\airbnb_webapp\brain-ui" -ForegroundColor Gray
Write-Host "npm run dev -- --host 0.0.0.0 --port 3000" -ForegroundColor Gray

Write-Host "`n=== TEST URLS (after starting services) ===" -ForegroundColor Cyan
Write-Host "Local testing:" -ForegroundColor White
Write-Host "- http://localhost" -ForegroundColor Gray
Write-Host "- http://localhost:8080" -ForegroundColor Gray  
Write-Host "- http://localhost:8000" -ForegroundColor Gray
Write-Host "- http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "External URLs (after DNS setup):" -ForegroundColor White  
Write-Host "- http://brain.xemgiadat.com" -ForegroundColor Gray
Write-Host "- http://webhook.xemgiadat.com" -ForegroundColor Gray
Write-Host "- http://api.xemgiadat.com" -ForegroundColor Gray
```

### STEP 5: Setup Cloudflare DNS  
```powershell
Write-Host "=== CLOUDFLARE DNS SETUP ===" -ForegroundColor Green

$publicIP = Get-Content "public-ip.txt" -ErrorAction SilentlyContinue
if (-not $publicIP) {
    $publicIP = "GET_FROM_STEP_1"
}

Write-Host "Your public IP: $publicIP" -ForegroundColor Yellow
Write-Host ""
Write-Host "Go to Cloudflare Dashboard → xemgiadat.com → DNS" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add these A records:" -ForegroundColor White
Write-Host "Name: brain     | IPv4: $publicIP | Proxy: DNS only" -ForegroundColor Gray
Write-Host "Name: webhook   | IPv4: $publicIP | Proxy: DNS only" -ForegroundColor Gray  
Write-Host "Name: api       | IPv4: $publicIP | Proxy: DNS only" -ForegroundColor Gray
Write-Host ""
Write-Host "Test DNS propagation (wait 5-10 minutes):" -ForegroundColor White
Write-Host "nslookup brain.xemgiadat.com" -ForegroundColor Gray
Write-Host "nslookup webhook.xemgiadat.com" -ForegroundColor Gray
Write-Host "nslookup api.xemgiadat.com" -ForegroundColor Gray
```