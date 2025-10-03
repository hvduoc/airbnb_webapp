# Railway Deployment - Zero Configuration

## 🚀 Easiest option - No server management needed

### 1. Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login và deploy
railway login
railway init
railway up
```

### 2. Railway sẽ tự động:
- Build và deploy ứng dụng
- Tạo public URL: https://airbnb-app-production.up.railway.app
- Handle SSL/HTTPS
- Auto-scaling
- Zero config needed

### 3. Custom Domain Setup trong Railway Dashboard
1. Go to: railway.app → Your Project → Settings → Domains
2. Add custom domains:
   ```
   brain.xemgiadat.com → brain-ui service
   webhook.xemgiadat.com → webhook service  
   api.xemgiadat.com → main-api service
   ```

### 4. Railway sẽ cho bạn CNAME values:
```
brain.xemgiadat.com → CNAME → xyz123.railway.app
webhook.xemgiadat.com → CNAME → abc456.railway.app  
api.xemgiadat.com → CNAME → def789.railway.app
```

### 5. Update Cloudflare DNS:
```
Type: CNAME
Name: brain
Target: xyz123.railway.app  ← Value từ Railway
TTL: Auto
Proxy: ⚫ DNS only (Let Railway handle SSL)
```

### 6. Final URLs (STABLE):
- https://brain.xemgiadat.com
- https://webhook.xemgiadat.com/webhook/github
- https://api.xemgiadat.com

## 💰 Cost: $5-20/month tùy usage
## 🎯 Setup time: 15 minutes
## 🛠️ Maintenance: Zero