<#
Location: runlocal/run-inspector.ps1
Purpose: Load .env.local into the current process environment and start MCP Inspector using runlocal/config.json
#>

param(
    [switch]$CliMode
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Set the settings file for Pydantic to use .env.local
[System.Environment]::SetEnvironmentVariable('SETTINGS_FILE', '.env.local', 'Process')

if (-not (Test-Path '.env.local')) {
    Write-Error '.env.local not found. Please create it (copy from .env.example)'
    exit 1
}

# Load .env.local lines into process environment (ignores empty lines and comments)
Get-Content .env.local | ForEach-Object {
    if (-not [string]::IsNullOrWhiteSpace($_) -and -not ($_.TrimStart()).StartsWith('#')) {
        $parts = $_ -split '=', 2
        if ($parts.Length -eq 2) {
            $name = $parts[0].Trim()
            # Trim whitespace and surrounding quotes (single or double)
            $value = $parts[1].Trim()
            if ($value.StartsWith('"') -and $value.EndsWith('"')) { $value = $value.Trim('"') }
            if ($value.StartsWith("'") -and $value.EndsWith("'")) { $value = $value.Trim("'") }
            [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
            Write-Host "Set env $name"
        }
    }
}

$cmd = 'npx @modelcontextprotocol/inspector --config runlocal/config.json --server local-server'
if ($CliMode) { $cmd += ' --cli --method tools/list' }

Write-Host "Starting MCP Inspector with config: runlocal/config.json"
Invoke-Expression $cmd
