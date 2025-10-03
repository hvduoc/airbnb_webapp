# ===================================================================
# AIRBNB WEBAPP - PROD-002 Docker Environment Setup
# ===================================================================
# Hướng dẫn khởi động Docker infrastructure cho development/production
# ===================================================================

Write-Host "🐳 AIRBNB WEBAPP - Docker Environment Setup" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Gray

# 1. Kiểm tra Docker Desktop status
Write-Host "`n📋 STEP 1: Kiểm tra Docker Desktop..." -ForegroundColor Yellow

$dockerService = Get-Service -Name "com.docker.service" -ErrorAction SilentlyContinue
if ($dockerService) {
    Write-Host "✅ Docker service found: $($dockerService.Status)" -ForegroundColor Green
    
    if ($dockerService.Status -eq "Stopped") {
        Write-Host "🚀 Starting Docker Desktop..." -ForegroundColor Yellow
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -WindowStyle Hidden
        Write-Host "⏳ Waiting for Docker to start (30s)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
} else {
    Write-Host "❌ Docker Desktop not found. Please install Docker Desktop first:" -ForegroundColor Red
    Write-Host "   Download: https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe" -ForegroundColor Red
    exit 1
}

# 2. Test Docker availability
Write-Host "`n📋 STEP 2: Testing Docker connectivity..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ $dockerVersion" -ForegroundColor Green
    } else {
        throw "Docker command not available"
    }
    
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Host "✅ $composeVersion" -ForegroundColor Green
    } else {
        throw "Docker Compose not available"
    }
} catch {
    Write-Host "❌ Docker not ready. Please ensure Docker Desktop is running." -ForegroundColor Red
    Write-Host "   - Open Docker Desktop manually" -ForegroundColor Red
    Write-Host "   - Wait for it to fully start" -ForegroundColor Red
    Write-Host "   - Then re-run this script" -ForegroundColor Red
    exit 1
}

# 3. Setup environment variables
Write-Host "`n📋 STEP 3: Environment Configuration..." -ForegroundColor Yellow

# Development environment variables
$env:POSTGRES_DB = "airbnb_dev"
$env:POSTGRES_USER = "airbnb_user"
$env:POSTGRES_PASSWORD = "dev_password_123"
$env:REDIS_PASSWORD = "dev_redis_123"
$env:SECRET_KEY = "dev_secret_key_for_jwt_tokens_change_in_production"
$env:ENVIRONMENT = "development"
$env:DEBUG = "true"

Write-Host "✅ Development environment variables set:" -ForegroundColor Green
Write-Host "   POSTGRES_DB: $env:POSTGRES_DB" -ForegroundColor Gray
Write-Host "   POSTGRES_USER: $env:POSTGRES_USER" -ForegroundColor Gray
Write-Host "   ENVIRONMENT: $env:ENVIRONMENT" -ForegroundColor Gray
Write-Host "   DEBUG: $env:DEBUG" -ForegroundColor Gray

# 4. Create required directories
Write-Host "`n📋 STEP 4: Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    "data\postgres",
    "data\redis", 
    "data\prometheus",
    "data\grafana",
    "logs",
    "uploads",
    "backups",
    "ssl"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📁 Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "📁 Exists: $dir" -ForegroundColor Gray
    }
}

# 5. Clean up any existing containers (development only)
Write-Host "`n📋 STEP 5: Cleaning up existing containers..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.dev.yml down --remove-orphans 2>$null
    Write-Host "✅ Cleaned up existing development containers" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ No existing containers to clean up" -ForegroundColor Gray
}

# 6. Remove obsolete version attribute from docker-compose files
Write-Host "`n📋 STEP 6: Updating Docker Compose files..." -ForegroundColor Yellow

$files = @("docker-compose.yml", "docker-compose.dev.yml")
foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match "version:.*") {
            $content = $content -replace "version:.*\r?\n", ""
            Set-Content -Path $file -Value $content -NoNewline
            Write-Host "✅ Removed version attribute from $file" -ForegroundColor Green
        } else {
            Write-Host "ℹ️ $file already up to date" -ForegroundColor Gray
        }
    }
}

# 7. Build and start development environment
Write-Host "`n📋 STEP 7: Building development environment..." -ForegroundColor Yellow
Write-Host "🏗️ Building containers (this may take a few minutes)..." -ForegroundColor Yellow

try {
    # Build containers
    docker-compose -f docker-compose.dev.yml build --no-cache
    Write-Host "✅ Container build completed" -ForegroundColor Green
    
    # Start services
    Write-Host "🚀 Starting development services..." -ForegroundColor Yellow
    docker-compose -f docker-compose.dev.yml up -d
    
    # Wait for services to be ready
    Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
    
    # Check service status
    $services = docker-compose -f docker-compose.dev.yml ps --format "table"
    Write-Host "`n📊 Service Status:" -ForegroundColor Cyan
    Write-Host $services -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Error during container build/start: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔧 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "   1. Ensure Docker Desktop is fully started" -ForegroundColor Gray
    Write-Host "   2. Check available disk space (Docker needs several GB)" -ForegroundColor Gray
    Write-Host "   3. Try running: docker system prune -f" -ForegroundColor Gray
    Write-Host "   4. Restart Docker Desktop and try again" -ForegroundColor Gray
    exit 1
}

# 8. Test application availability
Write-Host "`n📋 STEP 8: Testing application endpoints..." -ForegroundColor Yellow

$endpoints = @{
    "FastAPI Application" = "http://localhost:8000/docs"
    "Health Check" = "http://localhost:8000/health"
    "Database Admin (Adminer)" = "http://localhost:8080"
    "Prometheus Metrics" = "http://localhost:9090"
}

foreach ($name in $endpoints.Keys) {
    $url = $endpoints[$name]
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $name: $url" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $name: $url (Status: $($response.StatusCode))" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ $name: $url (Not accessible yet)" -ForegroundColor Red
    }
}

# 9. Display management commands
Write-Host "`n🎯 DEVELOPMENT ENVIRONMENT READY!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Gray
Write-Host "`n📝 Management Commands:" -ForegroundColor Cyan
Write-Host "   View logs:           docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor Gray
Write-Host "   Stop services:       docker-compose -f docker-compose.dev.yml down" -ForegroundColor Gray
Write-Host "   Restart services:    docker-compose -f docker-compose.dev.yml restart" -ForegroundColor Gray
Write-Host "   Shell access:        docker-compose -f docker-compose.dev.yml exec webapp bash" -ForegroundColor Gray
Write-Host "   Database access:     docker-compose -f docker-compose.dev.yml exec postgres psql -U airbnb_user -d airbnb_dev" -ForegroundColor Gray

Write-Host "`n🔗 Quick Access URLs:" -ForegroundColor Cyan
foreach ($name in $endpoints.Keys) {
    Write-Host "   $name`: $($endpoints[$name])" -ForegroundColor Gray
}

Write-Host "`n🐍 Python Management:" -ForegroundColor Cyan
Write-Host "   Use docker_manager.py for advanced container management" -ForegroundColor Gray
Write-Host "   python docker_manager.py health" -ForegroundColor Gray
Write-Host "   python docker_manager.py logs-webapp" -ForegroundColor Gray

Write-Host "`n🎉 Happy Development! 🚀" -ForegroundColor Green