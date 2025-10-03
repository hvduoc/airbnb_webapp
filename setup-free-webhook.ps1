# 15-Minute FREE Setup Script

Write-Host "🚀 Starting FREE webhook setup với ngrok + Cloudflare..."
Write-Host ""

# Step 1: Install ngrok
Write-Host "📦 Step 1: Installing ngrok..."
if (!(Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "Installing ngrok via Chocolatey..."
    choco install ngrok
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Chocolatey not found. Please download ngrok manually:"
        Write-Host "https://ngrok.com/download"
        Write-Host "Extract to a folder và add to PATH"
        exit 1
    }
} else {
    Write-Host "✅ ngrok already installed"
}
Write-Host ""

# Step 2: Ngrok auth setup
Write-Host "🔑 Step 2: Setup ngrok authentication..."
Write-Host "1. Go to: https://dashboard.ngrok.com/signup (free account)"
Write-Host "2. Get auth token từ: https://dashboard.ngrok.com/get-started/your-authtoken"
Write-Host "3. Run command: ngrok config add-authtoken YOUR_TOKEN"
Write-Host ""
$authSetup = Read-Host "Have you completed ngrok auth setup? (y/n)"
if ($authSetup -ne "y") {
    Write-Host "⚠️ Please complete ngrok auth setup first, then run this script again"
    exit 0
}
Write-Host ""

# Step 3: Start webhook listener
Write-Host "🎯 Step 3: Starting webhook listener..."
Write-Host "Running: uvicorn webhook_listener:app --reload --port 8080"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn webhook_listener:app --reload --port 8080"
Start-Sleep 3
Write-Host ""

# Step 4: Start ngrok
Write-Host "🌐 Step 4: Starting ngrok tunnel..."  
Write-Host "Running: ngrok http 8080"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 8080"
Start-Sleep 5
Write-Host ""

# Step 5: Get ngrok URL
Write-Host "📋 Step 5: Getting ngrok public URL..."
try {
    $ngrokApi = Invoke-RestMethod "http://127.0.0.1:4040/api/tunnels"
    $publicUrl = $ngrokApi.tunnels[0].public_url
    $domain = $publicUrl -replace "https://", ""
    
    Write-Host "✅ Ngrok URL: $publicUrl"
    Write-Host "📱 Domain: $domain"
    Write-Host ""
} catch {
    Write-Host "⚠️ Could not get ngrok URL automatically."
    Write-Host "Please check ngrok terminal for the public URL"
    Write-Host ""
}

# Step 6: Cloudflare instructions
Write-Host "☁️ Step 6: Update Cloudflare DNS..."
Write-Host "1. Go to: https://dash.cloudflare.com"
Write-Host "2. Select domain: xemgiadat.com"  
Write-Host "3. DNS → Records → Add/Edit:"
Write-Host ""
Write-Host "   Type: CNAME"
Write-Host "   Name: webhook"
if ($domain) {
    Write-Host "   Target: $domain"
} else {
    Write-Host "   Target: [copy từ ngrok terminal]"
}
Write-Host "   TTL: Auto"
Write-Host "   Proxy: ⚫ DNS only (IMPORTANT!)"
Write-Host ""

# Step 7: GitHub webhook config  
Write-Host "🐙 Step 7: Configure GitHub webhook..."
Write-Host "1. Go to: https://github.com/hvduoc/airbnb_webapp/settings/hooks"
Write-Host "2. Add webhook:"
Write-Host "   Payload URL: https://webhook.xemgiadat.com/webhook/github"
Write-Host "   Content type: application/json"
Write-Host "   Secret: [your choice - save it!]"
Write-Host "   Events: Push events"
Write-Host "   Active: ✓"
Write-Host ""

# Step 8: Test
Write-Host "🧪 Step 8: Test the setup..."
Write-Host "1. Make a small change to any file trong .brain/"
Write-Host "2. Commit và push to GitHub"
Write-Host "3. Check webhook listener terminal for incoming request"
Write-Host "4. Check ngrok web interface: http://localhost:4040"
Write-Host ""

Write-Host "🎉 FREE webhook setup complete!"
Write-Host ""
Write-Host "📋 Your URLs:"
Write-Host "   Webhook: https://webhook.xemgiadat.com/webhook/github"
Write-Host "   Brain UI: http://localhost:3000 (start with: npm run dev)"
Write-Host "   Ngrok Admin: http://localhost:4040"
Write-Host ""
Write-Host "⚠️ Remember: Ngrok URL changes every 8 hours or restart"
Write-Host "   You'll need to update Cloudflare DNS when it changes"
Write-Host ""
Write-Host "💡 Pro tip: Bookmark ngrok admin panel để check URL dễ dàng"