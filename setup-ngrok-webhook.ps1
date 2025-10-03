# Ngrok Setup cho GitHub Webhook Testing

# 1. Install ngrok
Write-Host "📦 Installing ngrok..."
Write-Host "Option 1: Via Chocolatey"
Write-Host "choco install ngrok"
Write-Host ""
Write-Host "Option 2: Manual download"  
Write-Host "Download từ: https://ngrok.com/download"
Write-Host "Extract và add to PATH"
Write-Host ""

# 2. Setup ngrok auth (optional nhưng recommended)
Write-Host "🔑 Setup ngrok authentication..."
Write-Host "1. Sign up tại: https://dashboard.ngrok.com/signup"
Write-Host "2. Get auth token từ: https://dashboard.ngrok.com/get-started/your-authtoken"
Write-Host "3. Run: ngrok config add-authtoken YOUR_TOKEN"
Write-Host ""

# 3. Start webhook listener
Write-Host "🚀 Starting webhook listener..."
Write-Host "uvicorn webhook_listener:app --reload --port 8080"
Write-Host ""

# 4. Start ngrok tunnel (in another terminal)
Write-Host "🌐 Starting ngrok tunnel..."
Write-Host "ngrok http 8080"
Write-Host ""
Write-Host "Ngrok sẽ show URL như:"
Write-Host "Forwarding    https://abc123.ngrok.io -> http://localhost:8080"
Write-Host ""

# 5. Configure GitHub webhook
Write-Host "⚙️  Configure GitHub webhook:"
Write-Host "1. Go to: https://github.com/hvduoc/airbnb_webapp/settings/hooks"
Write-Host "2. Click 'Add webhook'"
Write-Host "3. Payload URL: https://YOUR_NGROK_URL.ngrok.io/webhook/github"
Write-Host "4. Content type: application/json"
Write-Host "5. Secret: your_webhook_secret"
Write-Host "6. Events: Just push events"
Write-Host "7. Active: ✓"
Write-Host ""

# 6. Test the webhook
Write-Host "🧪 Testing webhook:"
Write-Host "1. Make a change to .brain/ folder"
Write-Host "2. Commit và push to GitHub"  
Write-Host "3. Check ngrok terminal for incoming request"
Write-Host "4. Check webhook listener logs"
Write-Host ""

Write-Host "⚠️  IMPORTANT NOTES:"
Write-Host "- Ngrok URL changes every restart (free tier)"
Write-Host "- For permanent URL, upgrade to ngrok Pro"
Write-Host "- Hoặc deploy to production server"
Write-Host ""
Write-Host "💡 Pro tip: Save ngrok URL vào .env file để dễ reference"