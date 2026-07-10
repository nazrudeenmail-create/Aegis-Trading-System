# ───────────────────────────────────────────────────────────────
# Aegis Trading System — Windows Development Environment Setup
# ───────────────────────────────────────────────────────────────
# This script sets up the full ATS development environment.
#
# It checks for required tools, installs dependencies,
# and verifies everything is ready for development.
#
# Usage:
#   .\scripts\setup.ps1
#
# Alternative — run individual steps:
#   .\scripts\setup.ps1 -BackendOnly
#   .\scripts\setup.ps1 -FrontendOnly
# ───────────────────────────────────────────────────────────────

param (
    [switch] $BackendOnly,
    [switch] $FrontendOnly
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Aegis Trading System — Development Setup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Check Required Tools ────────────────────────────

function Test-Command($cmd) {
    try {
        $null = Get-Command $cmd -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

Write-Host "[1/5] Checking required tools..." -ForegroundColor Yellow
Write-Host ""

$allOk = $true

if (-not $FrontendOnly) {
    $python = Test-Command "python"
    $pip = Test-Command "pip"
    if ($python) {
        $pyVer = (python --version) -replace "Python ", ""
        Write-Host "  Python  : $pyVer   OK" -ForegroundColor Green
    }
    else {
        Write-Host "  Python  : NOT FOUND   Install from https://www.python.org/downloads/" -ForegroundColor Red
        $allOk = $false
    }
    if ($pip) {
        Write-Host "  pip     : Found        OK" -ForegroundColor Green
    }
    else {
        Write-Host "  pip     : NOT FOUND   Install Python first" -ForegroundColor Red
        $allOk = $false
    }
}

if (-not $BackendOnly) {
    $node = Test-Command "node"
    $npm = Test-Command "npm"
    if ($node) {
        $nodeVer = (node --version) -replace "v", ""
        Write-Host "  Node.js : $nodeVer       OK" -ForegroundColor Green
    }
    else {
        Write-Host "  Node.js : NOT FOUND   Install from https://nodejs.org/ `(LTS v20+`)" -ForegroundColor Red
        $allOk = $false
    }
    if ($npm) {
        $npmVer = (npm --version)
        Write-Host "  npm     : $npmVer        OK" -ForegroundColor Green
    }
    else {
        Write-Host "  npm     : NOT FOUND   Install Node.js first" -ForegroundColor Red
        $allOk = $false
    }
}

$docker = Test-Command "docker"
if ($docker) {
    $dockerVer = (docker --version) -replace "Docker version ", ""
    Write-Host "  Docker  : $dockerVer" -ForegroundColor Green
}
else {
    Write-Host "  Docker  : NOT FOUND   Install Docker Desktop" -ForegroundColor Yellow
    Write-Host "            Docker is only needed if you want container-based development." -ForegroundColor Yellow
}

if (-not $allOk) {
    Write-Host ""
    Write-Host "  Please install the missing tools listed above, then re-run this script." -ForegroundColor Red
    exit 1
}

# ── Step 2: Backend Setup ───────────────────────────────────

if (-not $FrontendOnly) {
    Write-Host ""
    Write-Host "[2/5] Setting up backend..." -ForegroundColor Yellow

    Set-Location "$projectRoot\backend"

    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "venv")) {
        Write-Host "  Creating Python virtual environment..." -ForegroundColor Gray
        python -m venv venv
    }

    # Activate and install dependencies
    $venvActivate = ".\venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivate) {
        . $venvActivate
    }

    Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
    pip install -r requirements.txt --quiet

    # Copy .env if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Host "  Creating .env from .env.example..." -ForegroundColor Gray
        Copy-Item ".env.example" ".env"

        # Auto-generate SECRET_KEY if it's still the placeholder
        $envContent = Get-Content ".env" -Raw
        if ($envContent -match "SECRET_KEY=replace_with_random_secret") {
            $generatedKey = python -c "import secrets; print(secrets.token_hex(32))"
            $envContent = $envContent -replace "SECRET_KEY=replace_with_random_secret", "SECRET_KEY=$generatedKey"
            Set-Content ".env" $envContent -NoNewline
            Write-Host "  Auto-generated SECRET_KEY." -ForegroundColor Gray
        }

        Write-Host "  Edit backend\.env to configure your DATABASE_URL if needed." -ForegroundColor Yellow
    }

    Write-Host "  Backend setup complete." -ForegroundColor Green
}

# ── Step 3: Frontend Setup ──────────────────────────────────

if (-not $BackendOnly) {
    Write-Host ""
    Write-Host "[3/5] Setting up frontend..." -ForegroundColor Yellow

    Set-Location "$projectRoot\frontend"

    Write-Host "  Installing Node.js dependencies..." -ForegroundColor Gray
    npm install --silent

    # Copy .env if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Host "  Creating .env from .env.example..." -ForegroundColor Gray
        Copy-Item ".env.example" ".env"
    }

    Write-Host "  Frontend setup complete." -ForegroundColor Green
}

# ── Step 4: Verify Setup ────────────────────────────────────

Write-Host ""
Write-Host "[4/5] Verifying setup..." -ForegroundColor Yellow

Set-Location $projectRoot

if (-not $FrontendOnly) {
    Write-Host "  Testing Python imports..." -ForegroundColor Gray
    Set-Location "$projectRoot\backend"
    $importTest = python -c "from app.core.config import get_settings; from app.main import app; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Backend imports: OK" -ForegroundColor Green
    }
    else {
        Write-Host "  Backend imports: FAILED" -ForegroundColor Red
        Write-Host "  $importTest" -ForegroundColor Red
    }
}

# ── Step 5: Next Steps ──────────────────────────────────────

Set-Location $projectRoot

Write-Host ""
Write-Host "[5/5] Setup complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Start backend:" -ForegroundColor White
Write-Host "    cd backend" -ForegroundColor Gray
Write-Host "    uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  Start frontend (separate terminal):" -ForegroundColor White
Write-Host "    cd frontend" -ForegroundColor Gray
Write-Host "    npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  Open browser:" -ForegroundColor White
Write-Host "    Frontend: http://localhost:5173" -ForegroundColor Gray
Write-Host "    Backend : http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "  Docker (all services at once):" -ForegroundColor White
Write-Host "    docker compose up" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""