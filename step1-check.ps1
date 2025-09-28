# Home Server Quick Setup
Write-Host "=== CHECKING HOME SERVER ENVIRONMENT ===" -ForegroundColor Green

# Check public IP
Write-Host "Getting public IP..." -ForegroundColor Yellow
try {
    $publicIP = (Invoke-RestMethod -Uri "https://ipapi.co/ip/").Trim()
    Write-Host "✅ Public IP: $publicIP" -ForegroundColor Green
    $publicIP | Out-File -FilePath "public-ip.txt"
} catch {
    Write-Host "❌ Cannot get public IP. Check internet connection." -ForegroundColor Red
    exit 1
}

# Check local IP  
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.PrefixOrigin -eq "Dhcp" -and $_.IPAddress -notlike "169.254.*"}).IPAddress | Select-Object -First 1
if (-not $localIP) {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*"}).IPAddress | Select-Object -First 1
}
Write-Host "✅ Local IP: $localIP" -ForegroundColor Green

# Test connection
Write-Host "Testing internet connection..." -ForegroundColor Yellow
$testResult = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet
if ($testResult) {
    Write-Host "✅ Internet connection: OK" -ForegroundColor Green
} else {
    Write-Host "❌ Internet connection: FAILED" -ForegroundColor Red
}

Write-Host "`n=== ROUTER CONFIGURATION NEEDED ===" -ForegroundColor Cyan
Write-Host "Configure port forwarding on your router:" -ForegroundColor White
Write-Host "External Port -> Internal Address" -ForegroundColor Yellow
Write-Host "80 -> ${localIP}:80" -ForegroundColor Gray
Write-Host "443 -> ${localIP}:443" -ForegroundColor Gray  
Write-Host "8080 -> ${localIP}:8080" -ForegroundColor Gray
Write-Host "3000 -> ${localIP}:3000" -ForegroundColor Gray
Write-Host "8000 -> ${localIP}:8000" -ForegroundColor Gray

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "1. Router admin panel: http://192.168.1.1 (most common)" -ForegroundColor White
Write-Host "2. Configure port forwarding as shown above" -ForegroundColor White
Write-Host "3. Run: .\step2-firewall.ps1 (as Administrator)" -ForegroundColor White