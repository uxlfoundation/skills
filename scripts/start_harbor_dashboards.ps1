#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$JobsPort = 8080,
    [ValidateRange(1, 65535)]
    [int]$TasksPort = 8081,
    [string]$WslDistribution = 'Ubuntu',
    [switch]$NoWsl,
    [switch]$Restart,
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

    if (-not $Restart -and (Test-Dashboard -Port $Port)) {
        return 'already-running'
    }

    $stdout = Join-Path $logRoot "$Name.stdout.log"
    $stderr = Join-Path $logRoot "$Name.stderr.log"
    $pidFile = Join-Path $logRoot "$Name.pid"

    if ($NoWsl) {
        $harborCommand = Get-Command harbor -ErrorAction SilentlyContinue
        $harborExecutable = if ($harborCommand) {
            $harborCommand.Source
        } else {
            Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::ApplicationData)) `
                'uv\tools\harbor\Scripts\harbor.exe'
        }
        if (-not (Test-Path -LiteralPath $harborExecutable -PathType Leaf)) {
            throw 'Harbor was not found on the Windows PATH or in the standard uv tool directory. Omit -NoWsl to use Ubuntu WSL.'
        }

        if ($Restart -and (Test-Path -LiteralPath $pidFile -PathType Leaf)) {
            $recorded = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
            $recordedProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($recorded.pid)" `
                -ErrorAction SilentlyContinue
            if ($recordedProcess) {
                $sameExecutable = [string]::Equals(
                    $recordedProcess.ExecutablePath,
                    $recorded.executable_path,
                    [StringComparison]::OrdinalIgnoreCase
                )
                $sameCommand = [string]::Equals(
                    $recordedProcess.CommandLine,
                    $recorded.command_line,
                    [StringComparison]::Ordinal
                )
                if (-not $sameExecutable -or -not $sameCommand) {
                    throw "Refusing to stop PID $($recorded.pid) because it no longer matches the recorded Harbor process."
                }
                Stop-Process -Id $recorded.pid
            }
            [System.IO.File]::Delete($pidFile)
        } elseif ($Restart -and (Test-Dashboard -Port $Port)) {
            throw "Cannot safely restart the $Name dashboard because its recorded PID is missing. Stop that process once, then start this script again."
        }

        if (Test-Dashboard -Port $Port) {
            return 'already-running'
        }

        $arguments = @('view', $Folder, "--$Mode", '--host', '127.0.0.1', '--port', [string]$Port)
        Start-Process -FilePath $harborExecutable -ArgumentList $arguments -WindowStyle Hidden `
            -WorkingDirectory $repoRoot -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr | Out-Null
    } else {
        if ($Restart) {
            throw '-Restart is supported with -NoWsl so the launcher can verify the exact Harbor process before stopping it.'
        }
        if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
            throw 'wsl.exe was not found. Install Harbor natively or run with a configured WSL distribution.'
        }
        $harborProbe = & wsl.exe -d $WslDistribution -- bash -lc `
            'if command -v harbor >/dev/null 2>&1; then command -v harbor; elif [ -x "$HOME/.local/share/uxl-harbor/bin/harbor" ]; then readlink -f "$HOME/.local/share/uxl-harbor/bin/harbor"; fi'
        $harborExecutable = if ($harborProbe) {
            ([string]($harborProbe | Select-Object -First 1)).Trim()
        } else {
            ''
        }
        if ($LASTEXITCODE -ne 0 -or -not $harborExecutable) {
            throw "Harbor was not found in WSL distribution '$WslDistribution'."
        }
        Start-Process -FilePath 'wsl.exe' `
            -ArgumentList @(
                '-d', $WslDistribution,
                '--cd', "`"$repoRoot`"",
                '--', 'env', 'HARBOR_TELEMETRY=off',
                $harborExecutable, 'view', $Folder, "--$Mode",
                '--host', '127.0.0.1', '--port', [string]$Port
            ) `
            -WindowStyle Hidden -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr | Out-Null
    }

    Wait-Dashboard -Port $Port -Name $Name
    if ($NoWsl) {
        $listener = Get-NetTCPConnection -LocalPort $Port -State Listen | Select-Object -First 1
        $listenerProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
        [ordered]@{
            pid = $listener.OwningProcess
            executable_path = $listenerProcess.ExecutablePath
            command_line = $listenerProcess.CommandLine
        } | ConvertTo-Json -Compress | Set-Content -LiteralPath $pidFile -Encoding utf8
    }
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
