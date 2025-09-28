# GitHub Integration Setup Script

# This script helps setup GitHub integration for Brain System

# 1. GitHub Personal Access Token Setup
Write-Host "🔑 Setting up GitHub Personal Access Token..."
Write-Host "1. Go to: https://github.com/settings/tokens"
Write-Host "2. Generate new token (classic)"
Write-Host "3. Select scopes: repo, workflow, write:packages"
Write-Host "4. Copy token and run:"
Write-Host '   $env:GITHUB_TOKEN="your_token_here"'
Write-Host ""

# 2. Webhook Secret Generation
Write-Host "🔐 Generating webhook secret..."
$WebhookSecret = -join ((1..32) | ForEach {Get-Random -Maximum 62 | ForEach {[char][int]((97,65)[[bool](Get-Random -Maximum 2)] + (Get-Random -Maximum 26))}})
Write-Host "Generated secret: $WebhookSecret"
Write-Host "Save this to your environment:"
Write-Host "`$env:WEBHOOK_SECRET=`"$WebhookSecret`""
Write-Host ""

# 3. Update webhook_listener.py with authentication
Write-Host "🚀 Updating webhook listener..."
$WebhookCode = @"
import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="Brain System Webhook Listener")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

@app.post("/webhook/github")
async def github_webhook(request: Request):
    # Verify GitHub signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    body = await request.body()
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    # Handle push events to main branch
    if payload.get("ref") == "refs/heads/main":
        # Sync .brain/ files
        await sync_brain_files(payload)
        
        return {"status": "success", "message": "Brain files synced"}
    
    return {"status": "ignored", "message": "Not main branch"}

async def sync_brain_files(payload):
    """Sync .brain/ files from GitHub"""
    import subprocess
    import json
    
    try:
        # Pull latest changes
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # Log the sync
        with open(".brain/logs/sync_log.json", "a") as f:
            log_entry = {
                "timestamp": payload["head_commit"]["timestamp"],
                "commit": payload["head_commit"]["id"][:7],
                "message": payload["head_commit"]["message"],
                "author": payload["head_commit"]["author"]["name"]
            }
            f.write(json.dumps(log_entry) + "\n")
            
        print(f"✅ Synced brain files from commit: {payload['head_commit']['id'][:7]}")
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@app.get("/")
async def root():
    return {"message": "Brain System Webhook Listener", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "webhook_configured": bool(WEBHOOK_SECRET)}
"@

$WebhookCode | Out-File -FilePath "webhook_listener_enhanced.py" -Encoding UTF8
Write-Host "✅ Enhanced webhook listener created: webhook_listener_enhanced.py"
Write-Host ""

# 4. Setup instructions
Write-Host "📋 Next steps:"
Write-Host "1. Set environment variables:"
Write-Host '   $env:GITHUB_TOKEN="your_token_here"'
Write-Host "   `$env:WEBHOOK_SECRET=`"$WebhookSecret`""
Write-Host ""
Write-Host "2. Run enhanced webhook listener:"
Write-Host "   uvicorn webhook_listener_enhanced:app --reload --port 8080"
Write-Host ""  
Write-Host "3. Configure GitHub webhook:"
Write-Host "   Repo → Settings → Webhooks → Add webhook"
Write-Host "   Payload URL: http://your-server:8080/webhook/github"
Write-Host "   Content type: application/json"
Write-Host "   Secret: $WebhookSecret"
Write-Host "   Events: Just the push event"
Write-Host ""
Write-Host "4. Test the integration:"
Write-Host "   Make a change to .brain/ folder and push to GitHub"
Write-Host "   Check webhook listener logs for sync confirmation"

Write-Host ""
Write-Host "🧠 Your Brain System is ready for real-time GitHub collaboration! 🚀"