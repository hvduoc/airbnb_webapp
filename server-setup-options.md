# Quick Server Setup for xemgiadat.com Subdomains

## 🖥️ Server Options

### Option 1: VPS (Recommended) 
**DigitalOcean/Vultr/Linode: $5-10/month**

### Option 2: Home Server + Port Forwarding
**Chi phí: $0, cần IP tĩnh hoặc Dynamic DNS**

### Option 3: Cloud Platforms
**Railway/Render: $5-20/month, zero config**

## 🚀 Quick VPS Setup (Ubuntu 22.04)

### 1. Create VPS và get IP
```bash
# Sau khi tạo VPS, note lại IP address
# Ví dụ: 123.456.789.123
```

### 2. Initial Server Setup
```bash
# Connect via SSH
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Install essentials
apt install -y nginx python3 python3-pip python3-venv git curl ufw

# Setup firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw allow 3000  # Brain UI
ufw allow 8000  # FastAPI
ufw allow 8080  # Webhook
ufw --force enable
```

### 3. Deploy Applications
```bash
# Clone repository
cd /opt
git clone https://github.com/hvduoc/airbnb_webapp.git
cd airbnb_webapp

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup systemd services
sudo cp deployment/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable airbnb-api airbnb-webhook airbnb-brain
sudo systemctl start airbnb-api airbnb-webhook airbnb-brain
```

### 4. Configure Nginx
```bash
# Copy nginx configs
sudo cp deployment/nginx/* /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/xemgiadat-* /etc/nginx/sites-enabled/

# Test và reload
sudo nginx -t
sudo systemctl reload nginx
```

## 🏠 Home Server Option (Free)

### Requirements:
- Máy tính chạy 24/7 (PC/laptop/Raspberry Pi)
- Internet có IP tĩnh hoặc Dynamic DNS
- Router có thể port forwarding

### Setup Steps:
```bash
# 1. Cài Ubuntu/Windows với WSL
# 2. Install applications như VPS
# 3. Configure router port forwarding:
#    Port 80 → Your PC:80 (Nginx)
#    Port 443 → Your PC:443 (SSL)
```

### Router Port Forwarding:
```
External Port 80 → Internal IP:80
External Port 443 → Internal IP:443
```

## ☁️ Railway Deployment (Easiest)

### Super Simple:
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login và deploy
railway login
railway init
railway up

# 3. Setup custom domains trong Railway dashboard:
#    brain.xemgiadat.com → brain-ui service
#    webhook.xemgiadat.com → webhook service  
#    api.xemgiadat.com → main-api service
```

## 📊 Cost Comparison

| Option | Monthly Cost | Setup Time | Maintenance |
|--------|-------------|------------|-------------|
| DigitalOcean VPS | $6 | 2 hours | Medium |
| Vultr VPS | $5 | 2 hours | Medium |
| Railway | $5-20 | 30 minutes | Low |
| Home Server | $0 | 4 hours | High |
| Ngrok Pro | $8 | 5 minutes | Low |

## 🎯 Recommendation

### **For Production (Best):**
```
DigitalOcean VPS ($6/month) + Cloudflare
= Stable, fast, professional, full control
```

### **For Quick Start (Easiest):**
```
Railway ($5/month) + Cloudflare  
= Zero config, instant deployment, professional URLs
```

### **For Budget (Free):**
```
Home Server + Port Forwarding + Cloudflare
= $0 cost, requires technical setup
```

## 🚀 Next Steps

1. **Choose server option** (VPS recommended)
2. **Update DNS records** trong Cloudflare với server IP
3. **Deploy applications** 
4. **Test subdomain access**
5. **Configure GitHub webhook** với stable URL

**Which option do you prefer? Tôi sẽ hướng dẫn setup chi tiết!** 🎯