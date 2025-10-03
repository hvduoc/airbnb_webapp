# FREE Solution - Ngrok + Cloudflare với xemgiadat.com

## 🎯 Chi phí: $0 - Chỉ cần máy tính và domain có sẵn

### 1. Install Ngrok (Free tier)
```powershell
# Option 1: Via Chocolatey
choco install ngrok

# Option 2: Manual download
# Download từ: https://ngrok.com/download
# Extract và add to PATH
```

### 2. Setup Ngrok Auth (Free account)
```powershell
# Sign up free tại: https://dashboard.ngrok.com/signup
# Get auth token từ: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_FREE_TOKEN
```

### 3. Start Services
```powershell
# Terminal 1: Start webhook listener
uvicorn webhook_listener:app --reload --port 8080

# Terminal 2: Start ngrok tunnel  
ngrok http 8080

# Terminal 3: Start Brain UI
cd brain-ui
npm run dev
```

### 4. Ngrok sẽ show URL như:
```
Session Status    online
Account           your-email@gmail.com (Plan: Free)
Version           3.x.x
Region            Asia Pacific (ap)
Latency           45ms
Web Interface     http://127.0.0.1:4040

Forwarding        https://abc123-def456.ngrok-free.app -> http://localhost:8080

Connections       ttl     opn     rt1     rt5     p50     p90
                  0       0       0.00    0.00    0.00    0.00
```

### 5. Cloudflare DNS Setup
```
Type: CNAME
Name: webhook
Target: abc123-def456.ngrok-free.app  ← Copy từ ngrok
TTL: Auto
Proxy: ⚫ DNS only (QUAN TRỌNG: Không dùng Proxied)
```

### 6. GitHub Webhook Config
```
Payload URL: https://webhook.xemgiadat.com/webhook/github
Content type: application/json
Secret: your_webhook_secret
Events: Push events
```

### 7. Final URLs:
- **Webhook**: https://webhook.xemgiadat.com/webhook/github
- **Brain UI**: http://localhost:3000 (local)
- **Main API**: http://localhost:8000 (local)

## ⚠️ Free Tier Limitations:
- Ngrok URL thay đổi mỗi 8 giờ hoặc restart
- 40 connections/minute limit
- Warning page cho visitors (có thể skip)
- Phải update Cloudflare DNS khi URL đổi

## 🔄 Daily Workflow:
1. Start services: webhook + ngrok + brain UI
2. Check ngrok URL (nếu khác hôm qua)  
3. Update Cloudflare DNS nếu cần
4. Work normally với stable domain

## 🤖 Auto-update Script:
```powershell
# auto-update-webhook.ps1
$ngrokUrl = (Invoke-RestMethod "http://127.0.0.1:4040/api/tunnels").tunnels[0].public_url
$ngrokDomain = $ngrokUrl -replace "https://", ""

# Update Cloudflare DNS via API (optional)
# Requires Cloudflare API key
Write-Host "Current ngrok URL: $ngrokUrl"
Write-Host "Update Cloudflare CNAME: webhook.xemgiadat.com → $ngrokDomain"
```

## 💡 Pro Tips:
- Ngrok free reset mỗi 8h, thường stable trong ngày làm việc
- Bookmark ngrok web interface: http://localhost:4040
- Use VS Code terminal để manage multiple sessions
- Keep webhook listener chạy 24/7 nếu có thể

---

**🎉 FREE solution hoàn toàn! Chỉ cần time setup ban đầu.**