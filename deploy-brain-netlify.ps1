# Brain UI - Netlify Deployment Script

Write-Host "=== BRAIN UI NETLIFY DEPLOYMENT ===" -ForegroundColor Green

# Check if brain-ui exists
if (-not (Test-Path "brain-ui")) {
    Write-Host "❌ brain-ui folder not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found brain-ui folder" -ForegroundColor Green

# Copy brain data to public
Write-Host "📁 Copying brain data to public folder..." -ForegroundColor Yellow
$brainPublic = "brain-ui\public\brain"
if (-not (Test-Path $brainPublic)) {
    New-Item -ItemType Directory -Path $brainPublic -Force | Out-Null
}

# Copy .brain content
if (Test-Path ".brain") {
    Copy-Item -Recurse ".brain\*" $brainPublic -Force
    Write-Host "✅ Brain data copied to public folder" -ForegroundColor Green
} else {
    Write-Host "⚠️ .brain folder not found, using existing public data" -ForegroundColor Yellow
}

# Change to brain-ui directory
Set-Location brain-ui

# Check npm
Write-Host "📦 Checking Node.js and npm..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✅ Node.js: $nodeVersion, npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js or npm not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

# Build for production
Write-Host "🔨 Building for production..." -ForegroundColor Yellow
npm run build

Write-Host "✅ Build completed! dist/ folder ready for Netlify" -ForegroundColor Green
Write-Host ""
Write-Host "=== NETLIFY DEPLOYMENT OPTIONS ===" -ForegroundColor Cyan
Write-Host "Option 1 - Drag & Drop:" -ForegroundColor White
Write-Host "  1. Go to https://app.netlify.com/drop" -ForegroundColor Gray
Write-Host "  2. Drag the 'dist' folder to the page" -ForegroundColor Gray
Write-Host "  3. Get instant URL!" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2 - Netlify CLI:" -ForegroundColor White  
Write-Host "  1. npm install -g netlify-cli" -ForegroundColor Gray
Write-Host "  2. netlify login" -ForegroundColor Gray
Write-Host "  3. netlify deploy --prod --dir=dist" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3 - GitHub Integration:" -ForegroundColor White
Write-Host "  1. Push to GitHub: git push origin main" -ForegroundColor Gray
Write-Host "  2. Connect repository on Netlify dashboard" -ForegroundColor Gray
Write-Host "  3. Auto-deploy on every push!" -ForegroundColor Gray

# Back to original directory
Set-Location ..