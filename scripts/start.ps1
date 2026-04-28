# Smart startup script for Divvy (Windows PowerShell)
# Automatically detects if local PostgreSQL is needed

# Change to the project root directory
Set-Location -Path (Join-Path $PSScriptRoot "..")

Write-Host "Starting Divvy..." -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "No .env file found!" -ForegroundColor Yellow
    Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env with your configuration and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if DATABASE_URL is set to a remote database (Neon or other)
$envContent = Get-Content .env -Raw
if ($envContent -match "DATABASE_URL=.*neon\.tech") {
    Write-Host "Using remote database (Neon detected)" -ForegroundColor Green
    Write-Host "Starting backend and frontend only..." -ForegroundColor Cyan
    docker compose up $args
} elseif ($envContent -match "DATABASE_URL=[`"']?postgresql://.+@.+") {
    Write-Host "Using remote database" -ForegroundColor Green
    Write-Host "Starting backend and frontend only..." -ForegroundColor Cyan
    docker compose up $args
} else {
    Write-Host "No remote database detected" -ForegroundColor Yellow
    Write-Host "Starting with local PostgreSQL database..." -ForegroundColor Cyan
    docker compose --profile local-db up $args
}
