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
    $Pid = Get-Content $PidFile -ErrorAction Stop
    Write-Host "Found PID: $Pid" -ForegroundColor Cyan
} catch {
    Write-Host "Error reading PID file: $_" -ForegroundColor Red
    exit 1
}

# Try to stop the process
try {
    $Process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
    
    if ($Process) {
        Write-Host "Stopping process $Pid..." -ForegroundColor Yellow
        
        # Try graceful shutdown first
        $Process.CloseMainWindow() | Out-Null
        Start-Sleep -Seconds 2
        
        # Check if still running
        $Process.Refresh()
        if (-not $Process.HasExited) {
            Write-Host "Graceful shutdown failed, forcing termination..." -ForegroundColor Yellow
            Stop-Process -Id $Pid -Force
            Start-Sleep -Seconds 1
        }
        
        Write-Host "Server stopped successfully!" -ForegroundColor Green
    } else {
        Write-Host "Process $Pid is not running (may have already stopped)." -ForegroundColor Yellow
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
