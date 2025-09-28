# Temporary Solution - Ngrok với Custom Domain

## 🎯 Khi bạn chưa có server, dùng ngrok tạm

### 1. Install và chạy ngrok
```powershell
# Install ngrok
choco install ngrok

# Start your webhook listener
uvicorn webhook_listener:app --reload --port 8080

# In another terminal, start ngrok
ngrok http 8080
```

### 2. Ngrok sẽ cho URL như:
```
Forwarding  https://abc123-def456.ngrok.io -> http://localhost:8080
```

### 3. Cloudflare DNS Setup với ngrok
```
Type: CNAME
Name: webhook
Target: abc123-def456.ngrok.io  # Copy từ ngrok terminal
TTL: Auto  
Proxy: ⚫ DNS only (Important! Không dùng Proxied với ngrok)
```

### Final URL:
```
https://webhook.xemgiadat.com/webhook/github
→ points to → https://abc123-def456.ngrok.io/webhook/github
→ tunnels to → http://localhost:8080/webhook/github
```

### ⚠️ Limitations:
- Ngrok URL thay đổi mỗi lần restart
- Phải update Cloudflare DNS record mỗi lần
- Chỉ dùng tạm cho development

## 🔄 Workflow mỗi lần start development:
1. Start webhook: `uvicorn webhook_listener:app --reload --port 8080`
2. Start ngrok: `ngrok http 8080`
3. Copy ngrok URL (abc123.ngrok.io)
4. Update Cloudflare CNAME record
5. Test webhook: https://webhook.xemgiadat.com/webhook/github