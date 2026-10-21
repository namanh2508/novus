<#
.SYNOPSIS
    Orchestration script for local OWASP crAPI benchmark environment.
.DESCRIPTION
    Manages Docker Compose lifecycle for crAPI, performs container healthchecks,
    and validates network connectivity on port 8888.
.EXAMPLE
    .\deployments\run_crapi.ps1 -Action start
    .\deployments\run_crapi.ps1 -Action status
    .\deployments\run_crapi.ps1 -Action stop
#>

param(
    [ValidateSet("start", "stop", "status", "restart", "reset")]
    [string]$Action = "status"
)

$ComposeFile = Join-Path $PSScriptRoot "docker-compose.crapi.yml"
$TargetURL = "http://localhost:8888"

switch ($Action) {
    "start" {
        Write-Host "[*] Starting OWASP crAPI containers via Docker Compose..." -ForegroundColor Cyan
        docker compose -f $ComposeFile up -d
        Write-Host "[*] Waiting for services to initialize (15s)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15

        try {
            $resp = Invoke-WebRequest -Uri "$TargetURL/identity/api/auth/v1/health" -TimeoutSec 5 -UseBasicParsing
            Write-Host "[+] crAPI Identity Service is ONLINE (HTTP $($resp.StatusCode))" -ForegroundColor Green
        } catch {
            Write-Warning "[-] Service returned $($_.Exception.Message). Check 'docker compose -f $ComposeFile logs'."
        }
    }
    "status" {
        Write-Host "[*] Current crAPI container status:" -ForegroundColor Cyan
        docker compose -f $ComposeFile ps
    }
    "stop" {
        Write-Host "[*] Stopping crAPI containers..." -ForegroundColor Yellow
        docker compose -f $ComposeFile down
        Write-Host "[+] Containers stopped successfully." -ForegroundColor Green
    }
    "restart" {
        & $MyInvocation.MyCommand.Path -Action stop
        & $MyInvocation.MyCommand.Path -Action start
    }
    "reset" {
        Write-Host "[!] Wiping database volumes and resetting crAPI..." -ForegroundColor Red
        docker compose -f $ComposeFile down -v
        & $MyInvocation.MyCommand.Path -Action start
    }
}
