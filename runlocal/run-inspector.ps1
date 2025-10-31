<#
Location: runlocal/run-inspector.ps1
Purpose: Start MCP Inspector using HTTP transport with runlocal/config.json
Note: With HTTP transport, the server must be started separately before running the inspector
#>

param(
    [switch]$CliMode,
    [switch]$StartServer
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

# Check if server is running by testing the health endpoint
function Test-ServerRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10 -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Start server if requested
if ($StartServer) {
    Write-Host "Starting MCP server..." -ForegroundColor Cyan

    # Check if already running
    if (Test-ServerRunning) {
        Write-Host "Server is already running at http://localhost:8000" -ForegroundColor Yellow
    } else {
        # Set the settings file for Pydantic to use .env.local
        [System.Environment]::SetEnvironmentVariable('SETTINGS_FILE', '.env.local', 'Process')

        if (-not (Test-Path '.env.local')) {
            Write-Error '.env.local not found. Please create it (copy from .env.example)'
            exit 1
        }

        # Start the server in background
        Push-Location $RepoRoot
        & "$RepoRoot\scripts\run.ps1"
        Pop-Location

        # Wait for server to be ready
        Write-Host "Waiting for server to start..." -ForegroundColor Yellow
        $maxAttempts = 30
        $attempt = 0
        while (-not (Test-ServerRunning) -and $attempt -lt $maxAttempts) {
            Start-Sleep -Seconds 1
            $attempt++
            Write-Host "." -NoNewline
        }
        Write-Host ""

        if (-not (Test-ServerRunning)) {
            Write-Error "Server failed to start after $maxAttempts seconds"
            exit 1
        }

        Write-Host "Server is ready!" -ForegroundColor Green
        Write-Host ""
    }
}

# Check if server is running
if (-not (Test-ServerRunning)) {
    Write-Host "Error: MCP server is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "The HTTP transport requires the server to be running before starting the inspector." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To start the server:" -ForegroundColor Cyan
    Write-Host "  1. Run: .\scripts\run.ps1" -ForegroundColor White
    Write-Host "     (or use -StartServer flag to auto-start)" -ForegroundColor Gray
    Write-Host "  2. Wait for server to be ready at http://localhost:8000" -ForegroundColor White
    Write-Host "  3. Then run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "Quick start: .\runlocal\run-inspector.ps1 -StartServer" -ForegroundColor Cyan
    exit 1
}

Write-Host "MCP server is running at http://localhost:8000" -ForegroundColor Green
Write-Host ""

# Build inspector command
$cmd = 'npx @modelcontextprotocol/inspector --config runlocal/config.json --server local-server'
if ($CliMode) {
    # CLI mode for automated testing
    $cmd += ' --cli --method tools/call --tool-name get_github_user_info'
}

Write-Host "Starting MCP Inspector with config: runlocal/config.json" -ForegroundColor Cyan
Write-Host "Transport: HTTP (http://localhost:8000/mcp)" -ForegroundColor Gray
Write-Host ""

Invoke-Expression $cmd
