# Railway Setup Guide - FREE Alternative

## 🚀 Step-by-step Railway deployment

### 1. Sign up Railway
- Go to: https://railway.app
- Sign up với GitHub account (free)
- $5 free credit/month (no card needed initially)

### 2. Deploy từ GitHub
```bash
# Option A: CLI deployment
npm install -g @railway/cli
railway login
railway init
railway up

# Option B: Web dashboard
# 1. railway.app → "New Project"
# 2. "Deploy from GitHub repo"  
# 3. Select: hvduoc/airbnb_webapp
# 4. Railway tự động build & deploy
```

### 3. Configure Services
Railway sẽ detect automatically:
- **Main API**: FastAPI app (main.py)
- **Webhook**: Webhook listener (webhook_listener.py)  
- **Brain UI**: React app (brain-ui/)

### 4. Get Railway URLs
Railway provides:
```
Main API: https://airbnb-api-production-abc123.up.railway.app
Webhook: https://airbnb-webhook-production-def456.up.railway.app  
Brain UI: https://airbnb-brain-production-ghi789.up.railway.app
```

### 5. Custom Domain Setup
**Railway Dashboard → Settings → Domains:**
```
Add custom domain:
brain.xemgiadat.com → airbnb-brain-production-ghi789.up.railway.app
webhook.xemgiadat.com → airbnb-webhook-production-def456.up.railway.app
api.xemgiadat.com → airbnb-api-production-abc123.up.railway.app
```

Railway sẽ show CNAME values:
```
brain.xemgiadat.com → CNAME → xyz.railway.app
webhook.xemgiadat.com → CNAME → abc.railway.app
api.xemgiadat.com → CNAME → def.railway.app
```

### 6. Cloudflare DNS Update
```
Type: CNAME
Name: brain  
Target: xyz.railway.app (từ Railway)
TTL: Auto
Proxy: ⚫ DNS only (Let Railway handle SSL)
```

### 7. Environment Variables
Railway dashboard → Variables:
```
GITHUB_TOKEN=your_token
WEBHOOK_SECRET=your_secret
DATABASE_URL=sqlite:///./app.db
```

### 8. GitHub Webhook Config
```
Payload URL: https://webhook.xemgiadat.com/webhook/github
Content type: application/json
Secret: your_webhook_secret
Events: Push events
```

## 🎉 Final Result

### Professional URLs (STABLE FOREVER):
- Brain UI: https://brain.xemgiadat.com
- API: https://api.xemgiadat.com
- Webhook: https://webhook.xemgiadat.com/webhook/github

### Cost: $0-5/month (free tier covers small apps)
### Setup: 15 minutes  
### Maintenance: Zero

---

## 💡 Railway vs Other Platforms

| Feature | Railway | Heroku | Vercel | Netlify |
|---------|---------|---------|---------|---------|
| Free tier | $5/month | $0 | $0 | $0 |
| Custom domain | ✅ | ✅ | ✅ | ✅ |  
| Full-stack apps | ✅ | ✅ | ❌ | ❌ |
| Auto-deploy | ✅ | ✅ | ✅ | ✅ |
| Database | ✅ | Add-ons | ❌ | ❌ |
| Zero config | ✅ | ❌ | ✅ | ✅ |

**Railway = Best cho full-stack apps!** 🏆