#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[^/\s]+/[^/\s]+$')]
    [string]$Repository,

    [string]$WslDistribution = 'Ubuntu-24.04',
    [string]$RunnerRoot = '/home/uxlrunner/uxl-runner',
    [string]$RunnerName = "private-wsl-$env:COMPUTERNAME",
    [string]$Labels = 'uxl,sycl,gpu,intel-gpu,windows-wsl,personal-lab'
)

$ErrorActionPreference = 'Stop'
$repoUrl = "https://github.com/$Repository"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$stateRoot = Join-Path $repoRoot 'tmp\runner'
$safeRepository = $Repository -replace '[^A-Za-z0-9_.-]', '-'
$statePath = Join-Path $stateRoot "$safeRepository.json"
$stdout = Join-Path $stateRoot "$safeRepository.stdout.log"
$stderr = Join-Path $stateRoot "$safeRepository.stderr.log"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI is required.'
}
if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'WSL is required.'
}

$repo = gh repo view $Repository --json visibility,nameWithOwner | ConvertFrom-Json
if ($repo.visibility -ne 'PRIVATE') {
    throw "Refusing to attach a hardware runner to non-private repository $Repository."
}

& wsl.exe -d $WslDistribution -- bash -lc "test -f '$RunnerRoot/.runner'" | Out-Null
$configured = $LASTEXITCODE -eq 0
$runners = gh api "repos/$Repository/actions/runners" | ConvertFrom-Json
$match = $runners.runners | Where-Object name -EQ $RunnerName | Select-Object -First 1
$registrationMode = 'new'

if ($configured) {
    $localConfigText = (& wsl.exe -d $WslDistribution --exec cat "$RunnerRoot/.runner" | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $localConfigText) {
        throw "Could not read the existing runner configuration at $RunnerRoot."
    }
    $localConfig = $localConfigText.TrimStart([char]0xFEFF) | ConvertFrom-Json
    if ($localConfig.agentName -ne $RunnerName) {
        throw "Local runner name $($localConfig.agentName) does not match requested name $RunnerName."
    }
    if ($localConfig.gitHubUrl.TrimEnd('/') -ne $repoUrl) {
        throw "Local runner repository $($localConfig.gitHubUrl) does not match requested repository $repoUrl."
    }
    if (-not $match) {
        Write-Output "Clearing the completed ephemeral registration before creating the next one: $RunnerName"
        & wsl.exe -d $WslDistribution --cd $RunnerRoot --exec ./config.sh remove --local
        if ($LASTEXITCODE -ne 0) {
            throw "Could not clear the completed local registration at $RunnerRoot."
        }
        $configured = $false
        $registrationMode = 'renewed-after-ephemeral-job'
    } elseif ($match.status -eq 'online') {
        Write-Output "Ephemeral runner already online: $RunnerName"
        Write-Output "Repository: $repoUrl"
        exit 0
    } else {
        $registrationMode = 'resumed'
        Write-Output "Resuming existing offline ephemeral registration: $RunnerName"
    }
}

if (-not $configured) {
    if ($match) {
        throw "GitHub already has a runner named $RunnerName but $RunnerRoot is not configured. Remove the stale GitHub registration before retrying."
    }
    $registrationToken = gh api --method POST "repos/$Repository/actions/runners/registration-token" --jq .token
    if (-not $registrationToken) {
        throw 'GitHub did not return a runner registration token.'
    }

    $configure = @'
./config.sh --unattended --ephemeral --url "$PRIVATE_RUNNER_REPOSITORY_URL" --token "$PRIVATE_RUNNER_REGISTRATION_TOKEN" --name "$PRIVATE_RUNNER_NAME" --labels "$PRIVATE_RUNNER_LABELS" --work _work
configure_status=$?
unset PRIVATE_RUNNER_REGISTRATION_TOKEN
exit $configure_status
'@

    try {
        & wsl.exe -d $WslDistribution --cd $RunnerRoot --exec `
            env "PRIVATE_RUNNER_REGISTRATION_TOKEN=$registrationToken" `
            "PRIVATE_RUNNER_REPOSITORY_URL=$repoUrl" "PRIVATE_RUNNER_NAME=$RunnerName" `
            "PRIVATE_RUNNER_LABELS=$Labels" bash -lc $configure
        if ($LASTEXITCODE -ne 0) {
            throw 'Runner configuration failed.'
        }
    } finally {
        $registrationToken = $null
    }
}

& wsl.exe -d $WslDistribution -- bash -lc "test -f '$RunnerRoot/.runner'" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'Runner configuration did not produce a local registration.'
}

New-Item -ItemType Directory -Force -Path $stateRoot | Out-Null
$process = Start-Process -FilePath 'wsl.exe' `
    -ArgumentList @('-d', $WslDistribution, '--cd', $RunnerRoot, '--exec', './run.sh') `
    -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru

$online = $false
foreach ($attempt in 1..30) {
    Start-Sleep -Seconds 1
    if ($process.HasExited) {
        throw "Runner process exited before coming online. See $stderr."
    }
    $runners = gh api "repos/$Repository/actions/runners" | ConvertFrom-Json
    $match = $runners.runners | Where-Object name -EQ $RunnerName | Select-Object -First 1
    if ($match.status -eq 'online') {
        $online = $true
        break
    }
}
if (-not $online) {
    throw "Runner did not report online within 30 seconds. See $stderr."
}

[ordered]@{
    repository = $Repository
    runner_name = $RunnerName
    labels = $Labels
    wsl_distribution = $WslDistribution
    runner_root = $RunnerRoot
    registration_mode = $registrationMode
    windows_process_id = $process.Id
    started_at = (Get-Date).ToUniversalTime().ToString('o')
} | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8

Write-Output "Ephemeral runner online: $RunnerName"
Write-Output "Repository: $repoUrl"
Write-Output "State: $statePath"
