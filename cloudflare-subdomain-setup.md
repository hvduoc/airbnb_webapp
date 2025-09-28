# Cloudflare Subdomain Setup Guide

## 🌐 Tạo Subdomains trên Cloudflare Dashboard

### 1. Login vào Cloudflare Dashboard
- Go to: https://dash.cloudflare.com
- Select domain: xemgiadat.com

### 2. Tạo DNS Records
Vào DNS → Records → Add record:

```
Type: A
Name: brain
IPv4: YOUR_SERVER_IP  # IP của server bạn
TTL: Auto
Proxy: 🟠 Proxied (recommended)
```

```
Type: A  
Name: webhook
IPv4: YOUR_SERVER_IP
TTL: Auto
Proxy: 🟠 Proxied (recommended)
```

```
Type: A
Name: api  
IPv4: YOUR_SERVER_IP
TTL: Auto
Proxy: 🟠 Proxied (recommended)
```

### 3. SSL/TLS Configuration
- Go to SSL/TLS → Overview
- Set to "Full (strict)" or "Full"
- Enable "Always Use HTTPS"

### Final URLs:
- Brain UI: https://brain.xemgiadat.com
- API: https://api.xemgiadat.com  
- Webhook: https://webhook.xemgiadat.com/github

## 🔧 Server Configuration

### Nginx Reverse Proxy Setup:
```nginx
# /etc/nginx/sites-available/xemgiadat-brain
server {
    listen 80;
    server_name brain.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# /etc/nginx/sites-available/xemgiadat-webhook  
server {
    listen 80;
    server_name webhook.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# /etc/nginx/sites-available/xemgiadat-api
server {
    listen 80;
    server_name api.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable sites:
```bash
sudo ln -s /etc/nginx/sites-available/xemgiadat-brain /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/xemgiadat-webhook /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/xemgiadat-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔐 SSL Certificate (Cloudflare handles this automatically)

### If using Cloudflare Proxy (🟠 Proxied):
- SSL certificate tự động từ Cloudflare
- HTTPS enabled by default
- No additional setup needed

### If NOT using Proxy (⚫ DNS only):
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d brain.xemgiadat.com
sudo certbot --nginx -d webhook.xemgiadat.com  
sudo certbot --nginx -d api.xemgiadat.com
```

## 🧪 Testing

### Test DNS Resolution:
```bash
nslookup brain.xemgiadat.com
nslookup webhook.xemgiadat.com
nslookup api.xemgiadat.com
```

### Test HTTP Response:
```bash
curl -I https://brain.xemgiadat.com
curl -I https://webhook.xemgiadat.com
curl -I https://api.xemgiadat.com
```

## 📋 GitHub Webhook Configuration

### Final Webhook URL:
```
https://webhook.xemgiadat.com/webhook/github
```

### GitHub Repo Settings:
1. Go to: https://github.com/hvduoc/airbnb_webapp/settings/hooks
2. Add webhook:
   - Payload URL: `https://webhook.xemgiadat.com/webhook/github`
   - Content type: `application/json`
   - Secret: your_webhook_secret
   - Events: Push events
   - Active: ✓

## 🎯 Benefits của setup này:

✅ **Stable URLs**: Không bao giờ thay đổi
✅ **SSL/HTTPS**: Tự động từ Cloudflare  
✅ **DDoS Protection**: Cloudflare proxy
✅ **Analytics**: Cloudflare dashboard
✅ **Performance**: CDN caching
✅ **Professional**: Custom domain cho project

---

**🚀 Stable, secure, professional setup với domain riêng!**