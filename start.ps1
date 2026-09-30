# ---------------------------------------------------------------------------
#  Run the family tree on this computer - no Docker, no server needed.
#  Double-click start.cmd, or run:  powershell -ExecutionPolicy Bypass -File start.ps1
#
#  First run installs a Python environment and builds the interface (a few
#  minutes). After that it starts in seconds.
# ---------------------------------------------------------------------------

$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$venvDir = Join-Path $backend ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$requirements = Join-Path $backend "requirements.txt"
$nodeModules = Join-Path $frontend "node_modules"
$dist = Join-Path $frontend "dist"
$url = "http://localhost:8000"

function Step($message) {
    Write-Host ""
    Write-Host "==> $message" -ForegroundColor Green
}

function Fail($message) {
    Write-Host ""
    Write-Host $message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

function Run($exe, $arguments, $workdir) {
    if ($workdir) { Push-Location $workdir }
    try {
        & $exe @arguments
        $code = $LASTEXITCODE
    } finally {
        if ($workdir) { Pop-Location }
    }
    if ($code -ne 0) {
        Fail "That step failed: $exe $($arguments -join ' ')  (exit code $code)"
    }
}

# --- prerequisites ---------------------------------------------------------
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Fail "Python was not found.`nInstall Python 3.11 or newer from https://www.python.org/downloads/ and tick 'Add python.exe to PATH' during setup, then run this again."
}

$haveNode = [bool](Get-Command npm -ErrorAction SilentlyContinue)
$needNode = (-not (Test-Path $nodeModules)) -or (-not (Test-Path $dist))
if ($needNode -and -not $haveNode) {
    Fail "Node.js was not found.`nInstall Node 20 or newer from https://nodejs.org/ (use the 'LTS' button), then run this again."
}

# --- backend ---------------------------------------------------------------
$freshVenv = -not (Test-Path $venvPython)
if ($freshVenv) {
    Step "Creating the Python environment (first run only)"
    Run "python" @("-m", "venv", $venvDir)
    Run $venvPython @("-m", "pip", "install", "--disable-pip-version-check", "--quiet", "--upgrade", "pip") $null
}

Step "Installing backend dependencies"
Run $venvPython @("-m", "pip", "install", "--disable-pip-version-check", "--quiet", "-r", $requirements) $null

# --- interface -------------------------------------------------------------
if (-not (Test-Path $nodeModules)) {
    Step "Installing interface dependencies (first run only)"
    Run "npm" @("install", "--include=dev", "--no-audit", "--no-fund") $frontend
}

if (-not (Test-Path $dist)) {
    Step "Building the interface"
    Run "npm" @("run", "build") $frontend
}

# --- settings (set these before running to override) -----------------------
if (-not $env:SITE_TITLE)     { $env:SITE_TITLE = "Our Family Tree" }
if (-not $env:ADMIN_USERNAME) { $env:ADMIN_USERNAME = "admin" }
if (-not $env:ADMIN_PASSWORD) { $env:ADMIN_PASSWORD = "family123" }
if (-not $env:SEED_DEMO_DATA) { $env:SEED_DEMO_DATA = "true" }

Step "Starting the family tree"
Write-Host "   Address:  $url"
Write-Host "   Admin:    $($env:ADMIN_USERNAME) / $($env:ADMIN_PASSWORD)"
Write-Host "   Stop it:  press Ctrl+C in this window"
Write-Host "   Your data stays in: $(Join-Path $backend 'data')"
Write-Host ""

# Open the browser once the server has had a moment to start.
Start-Process -FilePath "powershell" -WindowStyle Hidden -ArgumentList @(
    "-NoProfile", "-Command", "Start-Sleep -Seconds 4; Start-Process '$url'"
) | Out-Null

& $venvPython -m uvicorn app.main:app --app-dir $backend --host 127.0.0.1 --port 8000
