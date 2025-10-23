# Run script for MCP OAuth Server (PowerShell)

Write-Host "=== Starting MCP OAuth Server ===" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Using default configuration." -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and configure OAuth credentials for full functionality."
    Write-Host ""
}

# Load environment variables if .env exists
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#].+?)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Run the server
Write-Host "Starting server..." -ForegroundColor Yellow
python -m mcp_server.main
