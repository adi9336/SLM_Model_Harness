# =====================================================================
# Setup Ollama & Local xLAM 1B Formatter on Windows
# =====================================================================
$ErrorActionPreference = "Continue"

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "   Two-Level Agent: Local Ollama & xLAM Setup" -ForegroundColor Cyan
Write-Host "=======================================================`n" -ForegroundColor Cyan

# 1. Check if Ollama is installed
$ollamaExe = (Get-Command "ollama.exe" -ErrorAction SilentlyContinue).Source
if (-not $ollamaExe) {
    $defaultPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    if (Test-Path $defaultPath) {
        $ollamaExe = $defaultPath
    }
}

if (-not $ollamaExe) {
    Write-Host "[1/3] Ollama not found. Installing Ollama for Windows..." -ForegroundColor Yellow
    $installer = "$env:TEMP\OllamaSetup.exe"
    if (-not (Test-Path $installer) -or ((Get-Item $installer).Length -lt 100MB)) {
        Write-Host "      Downloading Ollama installer from ollama.com..." -ForegroundColor Gray
        Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $installer -UseBasicParsing
    }
    Write-Host "      Running installer silently..." -ForegroundColor Gray
    Start-Process -FilePath $installer -ArgumentList "/silent" -Wait
    $ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    if (Test-Path $ollamaExe) {
        Write-Host "      Ollama installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "      Failed to locate installed Ollama. Please download from https://ollama.com" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/3] Ollama is already installed: $ollamaExe" -ForegroundColor Green
}

# Add to current process PATH
$ollamaDir = Split-Path -Parent $ollamaExe
if ($env:Path -notlike "*$ollamaDir*") {
    $env:Path = "$ollamaDir;" + $env:Path
}

# 2. Check if Ollama server daemon is running
Write-Host "`n[2/3] Checking Ollama server daemon (localhost:11434)..." -ForegroundColor Yellow
$isRunning = $false
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -UseBasicParsing -TimeoutSec 2
    if ($resp.StatusCode -eq 200) { $isRunning = $true }
} catch {}

if (-not $isRunning) {
    Write-Host "      Starting Ollama server daemon in background..." -ForegroundColor Gray
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "      Ollama daemon is now running on port 11434." -ForegroundColor Green
} else {
    Write-Host "      Ollama daemon is active on port 11434." -ForegroundColor Green
}

# 3. Pull xLAM 1B model
Write-Host "`n[3/3] Pulling local xLAM 1B tool-formatter model..." -ForegroundColor Yellow
Write-Host "      Model: allenporter/xlam:1b (lightweight, runs fast on CPU)..." -ForegroundColor Gray
& $ollamaExe pull allenporter/xlam:1b
& $ollamaExe cp allenporter/xlam:1b xlam:1b 2>$null
& $ollamaExe cp allenporter/xlam:1b xlam2:1b-fc-q4 2>$null

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "   Setup Complete! Local xLAM is ready on Ollama." -ForegroundColor Green
Write-Host "   Every run will now route Level 2 formatting locally!" -ForegroundColor Green
Write-Host "=======================================================`n" -ForegroundColor Cyan
