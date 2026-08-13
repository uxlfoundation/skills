#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$JobsPort = 8080,
    [ValidateRange(1, 65535)]
    [int]$TasksPort = 8081,
    [string]$WslDistribution = 'Ubuntu',
    [switch]$NoWsl,
    [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$logRoot = Join-Path $repoRoot 'tmp\dashboard'
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

function Test-Dashboard {
    param([int]$Port)

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/" -TimeoutSec 3
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Wait-Dashboard {
    param([int]$Port, [string]$Name)

    foreach ($attempt in 1..30) {
        if (Test-Dashboard -Port $Port) {
            return
        }
        Start-Sleep -Milliseconds 500
    }
    throw "$Name dashboard did not become ready on port $Port. See $logRoot."
}

function Start-HarborView {
    param(
        [string]$Name,
        [string]$Folder,
        [string]$Mode,
        [int]$Port
    )

    if (Test-Dashboard -Port $Port) {
        return 'already-running'
    }

    $stdout = Join-Path $logRoot "$Name.stdout.log"
    $stderr = Join-Path $logRoot "$Name.stderr.log"

    if ($NoWsl) {
        if (-not (Get-Command harbor -ErrorAction SilentlyContinue)) {
            throw 'Harbor was not found on the Windows PATH. Omit -NoWsl to use Ubuntu WSL.'
        }
        $arguments = @('view', $Folder, "--$Mode", '--host', '127.0.0.1', '--port', [string]$Port)
        Start-Process -FilePath 'harbor' -ArgumentList $arguments -WindowStyle Hidden `
            -WorkingDirectory $repoRoot -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr | Out-Null
    } else {
        if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
            throw 'wsl.exe was not found. Install Harbor natively or run with a configured WSL distribution.'
        }
        $repoLinux = (& wsl.exe -d $WslDistribution -- wslpath -a $repoRoot).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $repoLinux) {
            throw "Could not translate the repository path for WSL distribution '$WslDistribution'."
        }
        if ($repoLinux.Contains("'") -or $Folder.Contains("'")) {
            throw 'Repository and dashboard paths containing single quotes are not supported by the WSL launcher.'
        }
        $command = "cd '$repoLinux' && export HARBOR_TELEMETRY=off && exec harbor view '$Folder' --$Mode --host 127.0.0.1 --port $Port"
        Start-Process -FilePath 'wsl.exe' `
            -ArgumentList @('-d', $WslDistribution, '--', 'bash', '-lc', $command) `
            -WindowStyle Hidden -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr | Out-Null
    }

    Wait-Dashboard -Port $Port -Name $Name
    return 'started'
}

$jobsStatus = Start-HarborView -Name 'jobs' -Folder 'harbor-jobs' -Mode 'jobs' -Port $JobsPort
$tasksStatus = Start-HarborView -Name 'tasks' -Folder 'evaluation/harbor/tasks' -Mode 'tasks' -Port $TasksPort

$jobsUrl = "http://127.0.0.1:$JobsPort/"
$tasksUrl = "http://127.0.0.1:$TasksPort/"

if ($OpenBrowser) {
    Start-Process $jobsUrl
    Start-Process $tasksUrl
}

Write-Output "Results dashboard ($jobsStatus): $jobsUrl"
Write-Output "Task dashboard ($tasksStatus): $tasksUrl"
Write-Output "Logs: $logRoot"
