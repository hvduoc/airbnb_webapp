# Step 4: Start Services

Write-Host "=== STARTING NGINX ===" -ForegroundColor Green

# Start nginx
Write-Host "Starting Nginx..." -ForegroundColor Yellow
Start-Process -FilePath "C:\nginx\nginx.exe" -WindowStyle Hidden
Start-Sleep -Seconds 2

# Check if nginx started
$nginxProcess = Get-Process nginx -ErrorAction SilentlyContinue
if ($nginxProcess) {
    Write-Host "✅ Nginx started (PID: $($nginxProcess.Id))" -ForegroundColor Green
}
else {
    Write-Host "❌ Nginx failed to start" -ForegroundColor Red
}

Write-Host "`n=== MANUAL SERVICE START ===" -ForegroundColor Cyan
Write-Host "Now you need to start 3 services manually:" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 1 - Webhook Server:" -ForegroundColor Yellow
Write-Host "uvicorn webhook_listener:app --host 0.0.0.0 --port 8080 --reload" -ForegroundColor Gray
Write-Host ""

Write-Host "Terminal 2 - API Server:" -ForegroundColor Yellow  
Write-Host "uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Gray
Write-Host ""

Write-Host "Terminal 3 - Brain UI:" -ForegroundColor Yellow
Write-Host "cd brain-ui" -ForegroundColor Gray
Write-Host "npm run dev -- --host 0.0.0.0 --port 3000" -ForegroundColor Gray

Write-Host "`n=== TEST AFTER STARTING SERVICES ===" -ForegroundColor Cyan
Write-Host "Local URLs:" -ForegroundColor White
Write-Host "- http://localhost (should proxy to brain UI)" -ForegroundColor Gray
Write-Host "- http://localhost:8080 (webhook direct)" -ForegroundColor Gray  
Write-Host "- http://localhost:8000 (API direct)" -ForegroundColor Gray
Write-Host "- http://localhost:3000 (brain UI direct)" -ForegroundColor Gray

$publicIP = Get-Content "public-ip.txt" -ErrorAction SilentlyContinue
Write-Host "`nExternal URLs (after DNS setup):" -ForegroundColor White  
Write-Host "- http://brain.xemgiadat.com" -ForegroundColor Gray
Write-Host "- http://webhook.xemgiadat.com" -ForegroundColor Gray
Write-Host "- http://api.xemgiadat.com" -ForegroundColor Gray
Write-Host "`nYour public IP: $publicIP" -ForegroundColor Yellow
Write-Host "Configure Cloudflare DNS with this IP!" -ForegroundColor Yellow