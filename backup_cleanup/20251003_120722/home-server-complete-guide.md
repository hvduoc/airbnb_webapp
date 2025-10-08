# HOME SERVER SETUP - Tự chủ hoàn toàn

## 🎯 Mục tiêu: Dùng máy tính hiện tại làm production server

### ✅ Advantages của Home Server:
- **$0 cost**: Không phụ thuộc service thứ 3
- **Full control**: Toàn quyền kiểm soát
- **Privacy**: Data ở local, không lên cloud
- **Learning**: Hiểu rõ system administration
- **Scalable**: Upgrade hardware khi cần

### ⚠️ Requirements:
- Máy tính có thể chạy 24/7 (hoặc ít nhất giờ làm việc)
- Internet connection ổn định
- Router có thể port forwarding
- IP public (không bị ISP NAT)

---

## 🔍 STEP 1: Check Home Network Setup

### A. Kiểm tra Public IP
```powershell
# Check public IP
$publicIP = (Invoke-RestMethod -Uri "https://ipapi.co/ip/").Trim()
Write-Host "Your public IP: $publicIP"

# Save IP for later use
$publicIP | Out-File -FilePath "public-ip.txt"
```

### B. Check Internal IP
```powershell
# Get local IP của máy tính
$localIP = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp).IPAddress
Write-Host "Your local IP: $localIP"
```

### C. Test Internet Connection
```powershell
# Test connection quality
Test-NetConnection -ComputerName "8.8.8.8" -Port 53
Test-NetConnection -ComputerName "google.com" -Port 80
```

---

## 🚪 STEP 2: Router Port Forwarding

### A. Access Router Admin Panel
```
Common router addresses:
- 192.168.1.1 (most common)
- 192.168.0.1  
- 10.0.0.1
- 192.168.1.254

Login: admin/admin hoặc check router label
```

### B. Setup Port Forwarding Rules
```
External Port → Internal IP:Port
80 → YOUR_LOCAL_IP:80 (HTTP)
443 → YOUR_LOCAL_IP:443 (HTTPS)  
8080 → YOUR_LOCAL_IP:8080 (Webhook)
3000 → YOUR_LOCAL_IP:3000 (Brain UI)
8000 → YOUR_LOCAL_IP:8000 (API)

Example:
80 → 192.168.1.100:80
443 → 192.168.1.100:443
8080 → 192.168.1.100:8080
3000 → 192.168.1.100:3000  
8000 → 192.168.1.100:8000
```

### C. Test Port Forwarding
```powershell
# Test if ports are accessible from outside
# Use online tools:
# - https://www.yougetsignal.com/tools/open-ports/
# - https://portchecker.co/

# Or ask friend to test:
# curl http://YOUR_PUBLIC_IP:8080
```

---

## 🛡️ STEP 3: Windows Security Setup

### A. Windows Firewall Rules
```powershell
# Run as Administrator
# Allow incoming connections cho các ports cần thiết

# HTTP/HTTPS
New-NetFirewallRule -DisplayName "HTTP-In" -Direction Inbound -Port 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HTTPS-In" -Direction Inbound -Port 443 -Protocol TCP -Action Allow

# Application ports  
New-NetFirewallRule -DisplayName "Airbnb-Webhook" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Airbnb-Brain" -Direction Inbound -Port 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Airbnb-API" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow

# Verify rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Airbnb*"}
```

### B. Windows Defender Settings
```powershell
# Exclude project folder from real-time scanning
Add-MpPreference -ExclusionPath "D:\DUAN1\Airbnb\airbnb_webapp"

# Allow applications
Add-MpPreference -ExclusionProcess "python.exe"
Add-MpPreference -ExclusionProcess "node.exe"
Add-MpPreference -ExclusionProcess "uvicorn.exe"
```

---

## 🌐 STEP 4: Nginx Setup on Windows

### A. Download Nginx for Windows
```powershell
# Download nginx
$nginxUrl = "http://nginx.org/download/nginx-1.24.0.zip"
$nginxZip = "$env:TEMP\nginx.zip"

Invoke-WebRequest -Uri $nginxUrl -OutFile $nginxZip
Expand-Archive -Path $nginxZip -DestinationPath "C:\nginx"
```

### B. Nginx Configuration
```nginx
# C:\nginx\conf\nginx.conf
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
        server_name brain.xemgiadat.com YOUR_PUBLIC_IP;
        
        location / {
            proxy_pass http://brain_ui;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # API Server  
    server {
        listen 80;
        server_name api.xemgiadat.com;
        
        location / {
            proxy_pass http://api_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # Webhook Server
    server {
        listen 80;
        server_name webhook.xemgiadat.com;
        
        location / {
            proxy_pass http://webhook_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### C. Start Nginx as Windows Service
```powershell
# Install NSSM (Non-Sucking Service Manager)
choco install nssm

# Create nginx service
nssm install nginx "C:\nginx\nginx.exe"
nssm set nginx AppDirectory "C:\nginx"
nssm start nginx

# Verify service
Get-Service nginx
```

---

## ⚙️ STEP 5: Application Setup

### A. Bind Applications to All Interfaces
```powershell
# Start applications với external binding

# Terminal 1: Webhook
uvicorn webhook_listener:app --host 0.0.0.0 --port 8080 --reload

# Terminal 2: Main API  
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Brain UI
cd brain-ui
npm run dev -- --host 0.0.0.0 --port 3000
```

### B. Create Windows Services (Optional)
```powershell
# Install applications as Windows services để tự động start

# Webhook service
nssm install AirbnbWebhook "python.exe"
nssm set AirbnbWebhook AppDirectory "D:\DUAN1\Airbnb\airbnb_webapp"
nssm set AirbnbWebhook AppParameters "-m uvicorn webhook_listener:app --host 0.0.0.0 --port 8080"

# API service
nssm install AirbnbAPI "python.exe"  
nssm set AirbnbAPI AppDirectory "D:\DUAN1\Airbnb\airbnb_webapp"
nssm set AirbnbAPI AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 8000"

# Start services
nssm start AirbnbWebhook
nssm start AirbnbAPI
```

---

## ☁️ STEP 6: Cloudflare DNS Configuration

### A. DNS Records
```
Type: A
Name: brain
IPv4: YOUR_PUBLIC_IP (from step 1)
TTL: Auto
Proxy: ⚫ DNS only (vì chưa có SSL cert)

Type: A
Name: webhook  
IPv4: YOUR_PUBLIC_IP
TTL: Auto
Proxy: ⚫ DNS only

Type: A
Name: api
IPv4: YOUR_PUBLIC_IP  
TTL: Auto
Proxy: ⚫ DNS only
```

### B. Test DNS Resolution
```powershell
# Test DNS propagation
nslookup brain.xemgiadat.com
nslookup webhook.xemgiadat.com  
nslookup api.xemgiadat.com

# Should resolve to YOUR_PUBLIC_IP
```

---

## 🧪 STEP 7: Testing

### A. Local Testing
```powershell
# Test local access
curl http://localhost:8080/health
curl http://localhost:8000/
curl http://localhost:3000/

# Test nginx proxy
curl http://localhost/
```

### B. External Testing
```powershell  
# Test external access (from another network/phone 4G)
curl http://brain.xemgiadat.com
curl http://webhook.xemgiadat.com
curl http://api.xemgiadat.com

# Or use online tools:
# https://www.websiteplanet.com/webtools/uptime-checker/
```

### C. GitHub Webhook Test
```
1. GitHub repo → Settings → Webhooks
2. Add webhook:
   Payload URL: http://webhook.xemgiadat.com/webhook/github
   Content type: application/json
   Secret: your_secret
   Events: Push events
   
3. Test delivery trong webhook settings
4. Check local logs cho incoming requests
```

---

## 🚀 Final URLs:
- **Brain UI**: http://brain.xemgiadat.com  
- **API**: http://api.xemgiadat.com
- **Webhook**: http://webhook.xemgiadat.com/webhook/github

## 💡 Next Steps:
1. **SSL Certificate** setup (Let's Encrypt)
2. **Dynamic DNS** nếu IP thay đổi thường xuyên
3. **Backup strategy** cho data
4. **Monitoring** và log rotation
5. **Security hardening**

---

**🎉 Home server hoàn toàn tự chủ!** No dependencies on 3rd party services!