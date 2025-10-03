# Test GitHub Webhook System
# test-webhook-system.ps1

param(
    [string]$WebhookUrl = "http://localhost:8002",
    [switch]$TestAll,
    [switch]$TestManualSync,
    [switch]$TestGitHubPayload
)

$ErrorActionPreference = "Stop"

function Test-Service {
    Write-Host "🔍 Testing webhook service..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$WebhookUrl/" -Method GET
        Write-Host "✅ Service is running" -ForegroundColor Green
        Write-Host "   Status: $($response.status)" -ForegroundColor White
        Write-Host "   Brain dest: $($response.brain_dest)" -ForegroundColor White
        Write-Host "   Brain exists: $($response.brain_dest_exists)" -ForegroundColor White
        return $true
    }
    catch {
        Write-Host "❌ Service not accessible: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-ManualSync {
    Write-Host "🔄 Testing manual sync..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$WebhookUrl/api/sync/manual" -Method POST
        Write-Host "✅ Manual sync triggered" -ForegroundColor Green
        Write-Host "   Message: $($response.message)" -ForegroundColor White
        
        # Đợi 3 giây rồi kiểm tra status
        Start-Sleep -Seconds 3
        
        $status = Invoke-RestMethod -Uri "$WebhookUrl/api/sync/status" -Method GET
        if ($status.latest_sync) {
            Write-Host "✅ Sync completed" -ForegroundColor Green
            Write-Host "   Status: $($status.latest_sync.status)" -ForegroundColor White
            Write-Host "   Timestamp: $($status.latest_sync.timestamp)" -ForegroundColor White
        }
        
        return $true
    }
    catch {
        Write-Host "❌ Manual sync failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-GitHubWebhook {
    Write-Host "🐙 Testing GitHub webhook simulation..." -ForegroundColor Yellow
    
    # Tạo payload giả lập GitHub
    $payload = @{
        ref = "refs/heads/main"
        commits = @(
            @{
                id = "abc123def456"
                message = "Test webhook: Update brain data"
                author = @{
                    name = "Test User"
                    email = "test@example.com"
                }
                added = @(".brain/test.md")
                modified = @(".brain/SCOPE.md")
                removed = @()
            }
        )
    } | ConvertTo-Json -Depth 10
    
    try {
        # Tạo signature (nếu có secret)
        $secret = $env:GITHUB_WEBHOOK_SECRET
        if (-not $secret) {
            $secret = "your-secret-key-here"  # Default từ example
        }
        
        $hmac = New-Object System.Security.Cryptography.HMACSHA256
        $hmac.Key = [Text.Encoding]::UTF8.GetBytes($secret)
        $hashBytes = $hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($payload))
        $signature = "sha256=" + [Convert]::ToHexString($hashBytes).ToLower()
        
        $headers = @{
            'X-GitHub-Event' = 'push'
            'X-Hub-Signature-256' = $signature
            'Content-Type' = 'application/json'
        }
        
        $response = Invoke-RestMethod -Uri "$WebhookUrl/api/webhook" -Method POST -Body $payload -Headers $headers
        Write-Host "✅ Webhook accepted" -ForegroundColor Green
        Write-Host "   Message: $($response.message)" -ForegroundColor White
        
        # Đợi 5 giây để xử lý hoàn thành
        Start-Sleep -Seconds 5
        
        # Kiểm tra status
        $status = Invoke-RestMethod -Uri "$WebhookUrl/api/sync/status" -Method GET
        if ($status.latest_sync) {
            Write-Host "✅ Sync after webhook completed" -ForegroundColor Green
            Write-Host "   Status: $($status.latest_sync.status)" -ForegroundColor White
        }
        
        return $true
    }
    catch {
        Write-Host "❌ GitHub webhook test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-History {
    Write-Host "📊 Testing sync history..." -ForegroundColor Yellow
    
    try {
        $history = Invoke-RestMethod -Uri "$WebhookUrl/api/sync/history" -Method GET
        if ($history.history -and $history.history.Count -gt 0) {
            Write-Host "✅ Sync history available" -ForegroundColor Green
            Write-Host "   Total syncs: $($history.history.Count)" -ForegroundColor White
            
            $latest = $history.history[-1]
            Write-Host "   Latest sync: $($latest.timestamp)" -ForegroundColor White
            Write-Host "   Latest status: $($latest.status)" -ForegroundColor White
        } else {
            Write-Host "⚠️ No sync history found" -ForegroundColor Yellow
        }
        
        return $true
    }
    catch {
        Write-Host "❌ Failed to get history: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-BrainUIIntegration {
    Write-Host "🧠 Testing Brain UI integration..." -ForegroundColor Yellow
    
    # Kiểm tra file đích tồn tại
    $brainDir = ".\brain-ui\public\brain"
    if (Test-Path $brainDir) {
        $files = Get-ChildItem -Path $brainDir -Recurse -File
        Write-Host "✅ Brain public directory exists" -ForegroundColor Green
        Write-Host "   Files found: $($files.Count)" -ForegroundColor White
        
        # Liệt kê một số file mẫu
        $files | Select-Object -First 5 | ForEach-Object {
            $relativePath = $_.FullName.Substring((Resolve-Path $brainDir).Path.Length + 1)
            Write-Host "   - $relativePath" -ForegroundColor Gray
        }
        
        return $true
    } else {
        Write-Host "❌ Brain public directory not found" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "🚀 GitHub Webhook System Test Suite" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Test 1: Service health check
if (-not (Test-Service)) {
    $allPassed = $false
    Write-Host ""
    Write-Host "❌ Cannot continue - webhook service is not running" -ForegroundColor Red
    Write-Host "💡 Start the service first: .\scripts\start-webhook-service.ps1 -Development" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Manual sync
if ($TestManualSync -or $TestAll) {
    if (-not (Test-ManualSync)) {
        $allPassed = $false
    }
    Write-Host ""
}

# Test 3: GitHub webhook simulation
if ($TestGitHubPayload -or $TestAll) {
    if (-not (Test-GitHubWebhook)) {
        $allPassed = $false
    }
    Write-Host ""
}

# Test 4: History
if ($TestAll) {
    if (-not (Test-History)) {
        $allPassed = $false
    }
    Write-Host ""
}

# Test 5: Brain UI integration
if ($TestAll) {
    if (-not (Test-BrainUIIntegration)) {
        $allPassed = $false
    }
    Write-Host ""
}

# Summary
Write-Host "📋 Test Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "🎉 All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Webhook system is working correctly" -ForegroundColor Green
    Write-Host "✅ Ready for GitHub webhook integration" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Configure GitHub webhook in repository settings" -ForegroundColor White
    Write-Host "2. Use ngrok or deploy to expose webhook endpoint" -ForegroundColor White
    Write-Host "3. Test with real GitHub push events" -ForegroundColor White
} else {
    Write-Host "❌ Some tests failed" -ForegroundColor Red
    Write-Host "💡 Check the logs and fix issues before proceeding" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 Useful commands:" -ForegroundColor Cyan
Write-Host "  .\scripts\start-webhook-service.ps1 -Development  # Start service" -ForegroundColor White
Write-Host "  .\test-webhook-system.ps1 -TestAll               # Run all tests" -ForegroundColor White
Write-Host "  Get-Content webhook_sync.log -Tail 20 -Wait      # Watch logs" -ForegroundColor White