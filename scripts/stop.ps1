# Stop script for MCP OAuth Server (PowerShell)
# This script stops the background server process

$ErrorActionPreference = 'Stop'

Write-Host "=== Stopping MCP OAuth Server ===" -ForegroundColor Cyan
Write-Host ""

# Define PID file path
$PidFile = ".mcp-server.pid"

# Check if PID file exists
if (-not (Test-Path $PidFile)) {
    Write-Host "No PID file found. Server may not be running." -ForegroundColor Yellow
    Write-Host "PID file location: $PidFile" -ForegroundColor Gray
    exit 0
}

# Read PID from file
try {
    $ProcessPid = Get-Content $PidFile -ErrorAction Stop
    Write-Host "Found PID: $ProcessPid" -ForegroundColor Cyan
} catch {
    Write-Host "Error reading PID file: $_" -ForegroundColor Red
    exit 1
}

# Try to stop the process
try {
    $Process = Get-Process -Id $ProcessPid -ErrorAction SilentlyContinue

    if ($Process) {
    Write-Host "Stopping server (PID $PID_TO_STOP)..." -ForegroundColor Cyan
    Stop-Process -Id $PID_TO_STOP -Force

    # Wait for process to stop
    for ($local:i = 1; $i -le 10; $i++) {
        $local:process = Get-Process -Id $PID_TO_STOP -ErrorAction SilentlyContinue
        if (-not $process) {
            break
        }
        Start-Sleep -Seconds 1
    }

    Remove-Item -Path $PID_FILE -ErrorAction SilentlyContinue
    Write-Host "Server stopped" -ForegroundColor Green
    } else {
        Write-Host "Process $ProcessPid is not running (may have already stopped)." -ForegroundColor Yellow
    }

    # Remove PID file
    Remove-Item $PidFile -Force
    Write-Host "PID file removed." -ForegroundColor Gray

} catch {
    Write-Host "Error stopping process: $_" -ForegroundColor Red
    Write-Host "You may need to manually kill process $Pid" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Server shutdown complete." -ForegroundColor Cyan
