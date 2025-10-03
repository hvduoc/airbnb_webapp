# FREE Home Server Solution

## 🏠 Chi phí: $0 - Dùng máy tính hiện tại làm server

### Requirements:
- Máy tính có thể chạy 24/7 (hoặc ít nhất trong giờ làm việc)
- Internet có IP public (không bị NAT của ISP)
- Router có admin access để port forwarding

### 1. Check Public IP
```powershell
# Check public IP của bạn
Invoke-RestMethod -Uri "https://ipapi.co/ip/"
# Result: 123.456.789.101 ← Đây sẽ là YOUR_SERVER_IP
```

### 2. Router Port Forwarding Setup
**Vào router admin panel (thường 192.168.1.1):**
```
External Port 8080 → Internal IP của máy bạn:8080
External Port 3000 → Internal IP của máy bạn:3000  
External Port 8000 → Internal IP của máy bạn:8000

Example:
External 8080 → 192.168.1.100:8080 (webhook)
External 3000 → 192.168.1.100:3000 (brain UI)
External 8000 → 192.168.1.100:8000 (main API)
```

### 3. Windows Firewall Rules
```powershell
# Allow incoming connections
New-NetFirewallRule -DisplayName "Airbnb Webhook" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Airbnb Brain UI" -Direction Inbound -Port 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Airbnb API" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow
```

### 4. Cloudflare DNS Setup
```
Type: A
Name: webhook
IPv4: 123.456.789.101  ← Your public IP
TTL: Auto
Proxy: ⚫ DNS only (vì home connection không có SSL cert)
```

### 5. Start Services với external binding
```powershell
# Webhook (bind to all interfaces)
uvicorn webhook_listener:app --host 0.0.0.0 --port 8080

# Brain UI  
cd brain-ui
npm run dev -- --host 0.0.0.0 --port 3000

# Main API
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. Final URLs:
- **Webhook**: http://webhook.xemgiadat.com:8080/webhook/github
- **Brain UI**: http://brain.xemgiadat.com:3000
- **API**: http://api.xemgiadat.com:8000

### ⚠️ Considerations:
- IP có thể thay đổi (ISP dynamic IP)
- Cần máy chạy 24/7 để webhook hoạt động
- Không có SSL/HTTPS (chỉ HTTP)
- Upload bandwidth từ home thường chậm
- Security risk (expose ports to internet)

### 💡 Dynamic IP Solution (Free):
```powershell
# Use No-IP.com hoặc DuckDNS.org cho dynamic IP
# Install client để auto-update IP khi thay đổi

# No-IP client: https://www.noip.com/download
# DuckDNS client: https://www.duckdns.org/install.jsp
```

---

**🎯 Free nhưng technical complexity cao hơn**