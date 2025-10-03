# Step 3: Setup Nginx Proxy

Write-Host "=== SETTING UP NGINX ===" -ForegroundColor Green

# Download nginx
$nginxDir = "C:\nginx"
if (Test-Path $nginxDir) {
    Write-Host "Nginx already exists, skipping download..." -ForegroundColor Yellow
} else {
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
} else {
    Write-Host "❌ Nginx configuration error:" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
}

Write-Host "`nNext: Run .\step4-start.ps1" -ForegroundColor Cyan