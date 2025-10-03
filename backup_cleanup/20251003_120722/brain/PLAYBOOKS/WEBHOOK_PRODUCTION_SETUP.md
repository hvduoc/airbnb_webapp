# Production Webhook Setup Guide

## 🎯 Mục tiêu: Stable webhook URL không thay đổi

## 🌐 Option 1: VPS/Cloud Server (Recommended)

### Setup trên DigitalOcean/Vultr/AWS EC2:
```bash
# 1. Tạo server với public IP
# 2. Install requirements
sudo apt update
sudo apt install python3 python3-pip git nginx

# 3. Clone repository
git clone https://github.com/hvduoc/airbnb_webapp.git
cd airbnb_webapp

# 4. Setup Python environment  
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure nginx reverse proxy
sudo nano /etc/nginx/sites-available/webhook
```

### Nginx Config:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # hoặc IP address
    
    location /webhook/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Final Webhook URL:
```
http://your-domain.com/webhook/github
# hoặc  
http://123.456.789.123/webhook/github
```

## 🏠 Option 2: Home Server với Dynamic DNS

### Setup với No-IP/DuckDNS:
```bash
# 1. Sign up cho free dynamic DNS:
# - No-IP: https://www.noip.com
# - DuckDNS: https://www.duckdns.org

# 2. Create hostname như: yourname.ddns.net

# 3. Install dynamic DNS client trên router hoặc server
# 4. Configure port forwarding: Port 8080 → Your local server

# 5. Webhook URL sẽ là:
# http://yourname.ddns.net:8080/webhook/github
```

## ☁️ Option 3: Railway/Heroku (Zero Config)

### Deploy to Railway:
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login và deploy
railway login
railway init
railway up

# Webhook URL tự động: https://yourapp.railway.app/webhook/github
```

## 📋 Comparison Table

| Option | Cost | Stability | Setup Complexity | URL Example |
|--------|------|-----------|------------------|-------------|
| Ngrok (Free) | Free | ❌ Changes often | ⭐ Easy | `https://abc123.ngrok.io/webhook/github` |
| Ngrok Pro | $8/month | ✅ Stable | ⭐ Easy | `https://yourapp.ngrok.io/webhook/github` |
| VPS | $5-20/month | ✅ Very Stable | ⭐⭐⭐ Medium | `http://your-domain.com/webhook/github` |
| Railway | $5-20/month | ✅ Very Stable | ⭐ Easy | `https://yourapp.railway.app/webhook/github` |
| Home + DDNS | Free | ⭐⭐ Mostly Stable | ⭐⭐⭐ Medium | `http://yourname.ddns.net:8080/webhook/github` |

## 🎯 Recommendation cho dự án của bạn:

### **Phase 1: Development/Testing (Now)**
```powershell
# Use ngrok cho immediate testing
.\setup-ngrok-webhook.ps1
```

### **Phase 2: Production (Week 2-3)**  
```bash
# Deploy to Railway (easiest) hoặc VPS
# URL sẽ stable và không đổi
```

## 🔧 Environment Variables Setup

```bash
# .env file
WEBHOOK_URL=https://your-stable-domain.com/webhook/github
GITHUB_TOKEN=your_github_token
WEBHOOK_SECRET=your_webhook_secret

# GitHub webhook configuration chỉ cần update 1 lần
# sau đó sẽ stable forever
```

---

**💡 Bottom line: Webhook URL chỉ đổi khi BẠN đổi infrastructure, không phải lúc nào cũng thay đổi!**