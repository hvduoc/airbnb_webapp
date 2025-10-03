# VPS Server Creation Guide

## 🎯 Tạo server thật với IP cố định

### 1. Tạo VPS trên DigitalOcean (Recommended)

#### Step-by-step:
1. **Sign up**: https://digitalocean.com (có $200 credit cho new users)
2. **Create Droplet**:
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic ($6/month - 1GB RAM, 1 CPU, 25GB SSD)  
   - Region: Singapore (gần VN nhất)
   - Authentication: SSH Key hoặc Password
   - Hostname: airbnb-brain-server

3. **After creation, note down the IP**:
   ```
   Example: 165.227.123.45  ← Đây là YOUR_SERVER_IP
   ```

### 2. Cloudflare DNS Setup (với IP thật)
```
Type: A
Name: brain
IPv4: 165.227.123.45  ← YOUR_SERVER_IP từ bước 1
TTL: Auto
Proxy: 🟠 Proxied (Enable Cloudflare features)
```

```
Type: A  
Name: webhook
IPv4: 165.227.123.45  ← Same IP
TTL: Auto
Proxy: 🟠 Proxied
```

```
Type: A
Name: api
IPv4: 165.227.123.45  ← Same IP  
TTL: Auto
Proxy: 🟠 Proxied
```

### 3. Server Setup
```bash
# SSH vào server
ssh root@165.227.123.45

# Update system
apt update && apt upgrade -y

# Install requirements
apt install -y nginx python3 python3-pip python3-venv git

# Clone your repo
git clone https://github.com/hvduoc/airbnb_webapp.git
cd airbnb_webapp

# Setup Python
python3 -m venv venv
source venv/bin/activate  
pip install -r requirements.txt

# Start services
uvicorn main:app --host 0.0.0.0 --port 8000 &
uvicorn webhook_listener:app --host 0.0.0.0 --port 8080 &
cd brain-ui && npm install && npm run build
```

### 4. Nginx Configuration
```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/xemgiadat
```

```nginx
# Nginx config content
server {
    listen 80;
    server_name brain.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
    }
}

server {
    listen 80;  
    server_name webhook.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
    }
}

server {
    listen 80;
    server_name api.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/xemgiadat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Final URLs (STABLE FOREVER):
- Brain UI: https://brain.xemgiadat.com  
- Webhook: https://webhook.xemgiadat.com/webhook/github
- API: https://api.xemgiadat.com

## 💰 Cost: $6/month cho everything