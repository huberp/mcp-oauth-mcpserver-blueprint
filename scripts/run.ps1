# Run script for MCP OAuth Server (PowerShell)
# This script starts the server in the background and writes a PID file

param(
    [switch]$Foreground
)

$ErrorActionPreference = 'Stop'

Write-Host "=== Starting MCP OAuth Server ===" -ForegroundColor Cyan
Write-Host ""

# Define PID file path
$PidFile = ".mcp-server.pid"

# Check if server is already running
if (Test-Path $PidFile) {
    $OldPid = Get-Content $PidFile
    try {
        $Process = Get-Process -Id $OldPid -ErrorAction SilentlyContinue
        if ($Process) {
            Write-Host "Server is already running with PID $OldPid" -ForegroundColor Yellow
            Write-Host "Use scripts/stop.ps1 to stop it first." -ForegroundColor Yellow
            exit 1
        } else {
            # Process no longer exists, remove stale PID file
            Remove-Item $PidFile -Force
        }
    } catch {
        # PID file exists but process doesn't, remove it
        Remove-Item $PidFile -Force
    }
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Using default configuration." -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and configure OAuth credentials for full functionality."
    Write-Host ""
}

# Prepare environment variables
$EnvVars = @{}
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#].+?)=(.*)$') {
            $EnvVars[$matches[1]] = $matches[2]
        }
    }
}

# Build python command
$PythonCmd = "python"
if (Test-Path "venv\Scripts\python.exe") {
    $PythonCmd = "venv\Scripts\python.exe"
}

if ($Foreground) {
    # Run in foreground (interactive mode)
    Write-Host "Starting server in foreground mode..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Apply environment variables
    foreach ($key in $EnvVars.Keys) {
        [System.Environment]::SetEnvironmentVariable($key, $EnvVars[$key], "Process")
    }
    
    & $PythonCmd -m mcp_server.main
} else {
    # Run in background mode
    Write-Host "Starting server in background mode..." -ForegroundColor Yellow
    
    # Create a temporary script to run the server with environment variables
    $TempScript = [System.IO.Path]::GetTempFileName() + ".ps1"
    $ScriptContent = @"
# Set environment variables
"@
    foreach ($key in $EnvVars.Keys) {
        $value = $EnvVars[$key]
        $ScriptContent += "`n`$env:$key = '$value'"
    }
    $ScriptContent += "`n& '$PythonCmd' -m mcp_server.main"
    
    Set-Content -Path $TempScript -Value $ScriptContent
    
    # Start process in background
    $Process = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$TempScript`"" `
        -WindowStyle Hidden `
        -PassThru
    
    # Wait a moment to ensure process started
    Start-Sleep -Seconds 2
    
    # Check if process is still running
    if ($Process.HasExited) {
        Write-Host "Error: Server failed to start" -ForegroundColor Red
        Remove-Item $TempScript -Force -ErrorAction SilentlyContinue
        exit 1
    }
    
    # Save PID to file
    $Process.Id | Out-File -FilePath $PidFile -Encoding ASCII
    
    Write-Host "Server started successfully!" -ForegroundColor Green
    Write-Host "PID: $($Process.Id)" -ForegroundColor Cyan
    Write-Host "PID file: $PidFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Server endpoints:" -ForegroundColor Cyan
    Write-Host "  MCP:    http://localhost:8000/mcp" -ForegroundColor White
    Write-Host "  OAuth:  http://localhost:8000/oauth/authorize" -ForegroundColor White
    Write-Host "  Health: http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop the server, run: .\scripts\stop.ps1" -ForegroundColor Yellow
    
    # Clean up temp script after a delay (in background)
    Start-Job -ScriptBlock {
        param($path)
        Start-Sleep -Seconds 10
        Remove-Item $path -Force -ErrorAction SilentlyContinue
    } -ArgumentList $TempScript | Out-Null
}
