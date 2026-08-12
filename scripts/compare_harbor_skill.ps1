#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$TaskName,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^uxl-[a-z0-9-]+$')]
    [string]$SkillName,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$PreviousRef,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Model,

    [string]$Agent = 'codex',
    [ValidateRange(1, 100)]
    [int]$Attempts = 3,
    [ValidateRange(1, 100)]
    [int]$Concurrency = 1,
    [ValidateRange(0.0, 1.0)]
    [double]$VerifiedRewardFloor = 1.0,
    [string]$ReasoningEffort = 'medium',
    [string]$TaskPath = 'evaluation/harbor/tasks',
    [string]$ExtraInstructionPath = '',
    [string]$JobsDir = 'harbor-jobs',
    [string]$JobPrefix = '',
    [string]$ReportPath = '',
    [string]$DashboardBaseUrl = 'http://127.0.0.1:8080',
    [string]$WslDistribution = 'Ubuntu',
    [string[]]$AgentEnv = @(),
    [switch]$DisableExtraInstruction,
    [switch]$NoWsl,
    [switch]$DryRun,
    [switch]$FailOnRegression
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$temporaryRoot = $null
$previousTelemetry = [Environment]::GetEnvironmentVariable('HARBOR_TELEMETRY', 'Process')
$previousPythonUtf8 = [Environment]::GetEnvironmentVariable('PYTHONUTF8', 'Process')

function Invoke-CheckedGit {
    param([string[]]$Arguments)

    $output = & git -C $repoRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed:`n$($output -join [Environment]::NewLine)"
    }
    return $output
}

function Get-HostPath {
    param([string]$PathValue)

    if ([IO.Path]::IsPathRooted($PathValue)) {
        return [IO.Path]::GetFullPath($PathValue)
    }
    return [IO.Path]::GetFullPath((Join-Path $repoRoot $PathValue))
}

function Get-ArgumentDisplay {
    param([string[]]$Arguments)

    $parts = [Collections.Generic.List[string]]::new()
    for ($index = 0; $index -lt $Arguments.Count; $index++) {
        $argument = $Arguments[$index]
        if ($index -gt 0 -and $Arguments[$index - 1] -eq '--agent-env') {
            $key = ($argument -split '=', 2)[0]
            $argument = "$key=<redacted>"
        }
        if ($argument -match '[\s"]') {
            $parts.Add('"' + $argument.Replace('"', '\"') + '"')
        } else {
            $parts.Add($argument)
        }
    }
    return $parts -join ' '
}

function Get-DirectoryDigest {
    param([string]$Directory)

    $root = [IO.Path]::GetFullPath($Directory).TrimEnd('\', '/')
    $entries = foreach ($file in Get-ChildItem -LiteralPath $root -File -Recurse | Sort-Object FullName) {
        $relative = $file.FullName.Substring($root.Length + 1).Replace('\', '/')
        $fileHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$relative $fileHash"
    }
    $bytes = [Text.Encoding]::UTF8.GetBytes(($entries -join "`n"))
    $hasher = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $hasher.Dispose()
    }
}

try {
    [Environment]::SetEnvironmentVariable('HARBOR_TELEMETRY', 'off', 'Process')
    # Harbor 0.20 reads Codex JSONL with Python's default text encoding. Force
    # UTF-8 so native Windows runs retain trajectories and token accounting.
    [Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'Process')

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'git is required but was not found on PATH.'
    }
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw 'python is required but was not found on PATH.'
    }

    $taskRootHost = Get-HostPath $TaskPath
    $taskHost = Join-Path $taskRootHost $TaskName
    $candidateSkillHost = Join-Path (Join-Path $repoRoot 'skills') $SkillName
    if (-not (Test-Path -LiteralPath (Join-Path $taskHost 'task.toml') -PathType Leaf)) {
        throw "Harbor task was not found: $taskHost"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $candidateSkillHost 'SKILL.md') -PathType Leaf)) {
        throw "Candidate skill was not found: $candidateSkillHost"
    }

    if (-not $DisableExtraInstruction -and -not $ExtraInstructionPath) {
        $defaultExtraInstruction = "evaluation/harbor/instructions/use-$SkillName.md"
        if (Test-Path -LiteralPath (Get-HostPath $defaultExtraInstruction) -PathType Leaf) {
            $ExtraInstructionPath = $defaultExtraInstruction
        }
    }
    $extraInstructionHost = $null
    if (-not $DisableExtraInstruction -and $ExtraInstructionPath) {
        $extraInstructionHost = Get-HostPath $ExtraInstructionPath
        if (-not (Test-Path -LiteralPath $extraInstructionHost -PathType Leaf)) {
            throw "Extra instruction was not found: $extraInstructionHost"
        }
    }

    $previousCommit = @(Invoke-CheckedGit @('rev-parse', '--verify', "$PreviousRef^{commit}"))[-1].Trim()
    Invoke-CheckedGit @('cat-file', '-e', "${previousCommit}:skills/$SkillName/SKILL.md") | Out-Null
    $previousTree = @(Invoke-CheckedGit @('rev-parse', "${previousCommit}:skills/$SkillName"))[-1].Trim()
    $headCommit = @(Invoke-CheckedGit @('rev-parse', 'HEAD'))[-1].Trim()
    $candidateTree = @(Invoke-CheckedGit @('rev-parse', "HEAD:skills/$SkillName"))[-1].Trim()
    $candidateDigest = Get-DirectoryDigest $candidateSkillHost
    $candidateChanges = @(Invoke-CheckedGit @('status', '--porcelain', '--', "skills/$SkillName"))
    $candidateDirty = $candidateChanges.Count -gt 0 -and $candidateChanges[0].Trim().Length -gt 0
    $previousDescriptor = "$PreviousRef@$previousCommit (tree $previousTree)"
    $candidateDescriptor = if ($candidateDirty) {
        "working-tree@$headCommit (dirty; content sha256 $candidateDigest; HEAD tree $candidateTree)"
    } else {
        "working-tree@$headCommit (content sha256 $candidateDigest; tree $candidateTree)"
    }

    $taskDigest = Get-DirectoryDigest $taskHost
    $taskDescriptor = "working-tree path $taskHost (content sha256 $taskDigest)"
    $repoPrefix = $repoRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if ($taskHost.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        $taskRelative = $taskHost.Substring($repoPrefix.Length).Replace('\', '/')
        $taskTreeOutput = & git -C $repoRoot rev-parse "HEAD:$taskRelative" 2>$null
        if ($LASTEXITCODE -eq 0 -and $taskTreeOutput) {
            $taskTree = @($taskTreeOutput)[-1].Trim()
            $taskChanges = @(Invoke-CheckedGit @('status', '--porcelain', '--', $taskRelative))
            $taskDirty = $taskChanges.Count -gt 0 -and $taskChanges[0].Trim().Length -gt 0
            $taskDescriptor = if ($taskDirty) {
                "working-tree@$headCommit (dirty; content sha256 $taskDigest; HEAD tree $taskTree)"
            } else {
                "working-tree@$headCommit (content sha256 $taskDigest; tree $taskTree)"
            }
        }
    }

    $directHarbor = Get-Command harbor -ErrorAction SilentlyContinue
    $uvToolHarbor = $null
    if (-not $directHarbor -and
        [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT -and
        $env:APPDATA) {
        $uvToolHarbor = Join-Path $env:APPDATA 'uv\tools\harbor\Scripts\harbor.exe'
        if (-not (Test-Path -LiteralPath $uvToolHarbor -PathType Leaf)) {
            $uvToolHarbor = $null
        }
    }
    $useWsl = $false
    $harborExecutable = $null
    $repoForHarbor = $repoRoot
    if ($directHarbor) {
        $harborExecutable = $directHarbor.Source
    } elseif ($uvToolHarbor) {
        $harborExecutable = $uvToolHarbor
    } elseif (-not $NoWsl -and (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
        $useWsl = $true
        $harborExecutable = (& wsl.exe -d $WslDistribution -- bash -lc 'command -v harbor').Trim()
        if ($LASTEXITCODE -ne 0 -or -not $harborExecutable) {
            throw "Harbor was not found in WSL distribution '$WslDistribution'."
        }
        $repoPathForWslpath = $repoRoot.Replace('\', '/')
        $repoForHarbor = (& wsl.exe -d $WslDistribution -- wslpath -a $repoPathForWslpath).Trim()
    } else {
        throw 'Harbor was not found on PATH, and no usable WSL fallback is available.'
    }

    function Convert-ToHarborPath {
        param([string]$HostPath)

        $fullPath = [IO.Path]::GetFullPath($HostPath)
        if (-not $useWsl) {
            return $fullPath
        }
        $pathForWslpath = $fullPath.Replace('\', '/')
        $converted = (& wsl.exe -d $WslDistribution -- wslpath -a $pathForWslpath).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $converted) {
            throw "Could not convert path for WSL: $fullPath"
        }
        return $converted
    }

    $effectiveAgentEnv = [Collections.Generic.List[string]]::new()
    $agentEnvKeys = @{}
    foreach ($entry in $AgentEnv) {
        if ($entry -notmatch '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
            throw "Agent environment entries must use KEY=VALUE syntax: $entry"
        }
        $key = $Matches[1]
        $agentEnvKeys[$key.ToUpperInvariant()] = $true
        $effectiveAgentEnv.Add($entry)
    }

    if ($Agent -eq 'codex' -and -not $agentEnvKeys.ContainsKey('CODEX_AUTH_JSON_PATH')) {
        $userProfile = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
        $codexAuthHost = Join-Path (Join-Path $userProfile '.codex') 'auth.json'
        if (Test-Path -LiteralPath $codexAuthHost -PathType Leaf) {
            $codexAuthForHarbor = Convert-ToHarborPath $codexAuthHost
            $effectiveAgentEnv.Add("CODEX_AUTH_JSON_PATH=$codexAuthForHarbor")
            $agentEnvKeys['CODEX_AUTH_JSON_PATH'] = $true
        }
    }

    foreach ($proxyName in @('HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY')) {
        $proxyValue = [Environment]::GetEnvironmentVariable($proxyName, 'Process')
        if ($proxyValue -and -not $agentEnvKeys.ContainsKey($proxyName)) {
            $effectiveAgentEnv.Add("$proxyName=$proxyValue")
            $effectiveAgentEnv.Add("$($proxyName.ToLowerInvariant())=$proxyValue")
            $agentEnvKeys[$proxyName] = $true
        }
    }

    $timestamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
    if (-not $JobPrefix) {
        $JobPrefix = "$TaskName-$timestamp"
    }
    $JobPrefix = $JobPrefix -replace '[^A-Za-z0-9._-]', '-'
    $jobNames = [ordered]@{
        NoSkill = "$JobPrefix-noskill"
        Previous = "$JobPrefix-previous"
        Candidate = "$JobPrefix-candidate"
    }
    $jobsDirHost = Get-HostPath $JobsDir
    foreach ($jobName in $jobNames.Values) {
        if (Test-Path -LiteralPath (Join-Path $jobsDirHost $jobName)) {
            throw "Job directory already exists; choose another -JobPrefix: $(Join-Path $jobsDirHost $jobName)"
        }
    }

    if (-not $ReportPath) {
        $ReportPath = Join-Path $JobsDir "$JobPrefix-comparison.md"
    }
    $reportHost = Get-HostPath $ReportPath
    if (Test-Path -LiteralPath $reportHost) {
        throw "Comparison report already exists: $reportHost"
    }

    $temporaryBase = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    $temporaryRoot = Join-Path $temporaryBase ("uxl-harbor-comparison-" + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $temporaryRoot | Out-Null
    $archivePath = Join-Path $temporaryRoot 'previous-skill.zip'
    $archiveOutput = & git -C $repoRoot archive --format=zip "--output=$archivePath" $previousCommit "skills/$SkillName" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Could not archive previous skill:`n$($archiveOutput -join [Environment]::NewLine)"
    }
    Expand-Archive -LiteralPath $archivePath -DestinationPath $temporaryRoot
    $previousSkillHost = Join-Path (Join-Path $temporaryRoot 'skills') $SkillName
    $candidateSkillSnapshotHost = Join-Path $temporaryRoot 'candidate-skill'
    Copy-Item -LiteralPath $candidateSkillHost -Destination $candidateSkillSnapshotHost -Recurse

    $taskPathForHarbor = Convert-ToHarborPath $taskRootHost
    $jobsDirForHarbor = Convert-ToHarborPath $jobsDirHost
    $candidateSkillForHarbor = Convert-ToHarborPath $candidateSkillSnapshotHost
    $previousSkillForHarbor = Convert-ToHarborPath $previousSkillHost
    $extraInstructionForHarbor = if ($extraInstructionHost) {
        Convert-ToHarborPath $extraInstructionHost
    } else {
        $null
    }

    function New-HarborArguments {
        param(
            [string]$JobName,
            [string]$SkillPath
        )

        $arguments = [Collections.Generic.List[string]]::new()
        foreach ($value in @(
            '--path', $taskPathForHarbor,
            '--include-task-name', $TaskName,
            '--agent', $Agent,
            '--model', $Model,
            '--n-attempts', $Attempts.ToString(),
            '--job-name', $JobName,
            '--jobs-dir', $jobsDirForHarbor,
            '--n-concurrent', $Concurrency.ToString()
        )) {
            $arguments.Add($value)
        }
        if ($ReasoningEffort) {
            $arguments.Add('--agent-kwarg')
            $arguments.Add("reasoning_effort=$ReasoningEffort")
        }
        foreach ($entry in $effectiveAgentEnv) {
            $arguments.Add('--agent-env')
            $arguments.Add($entry)
        }
        if ($SkillPath) {
            $arguments.Add('--skill')
            $arguments.Add($SkillPath)
            if ($extraInstructionForHarbor) {
                $arguments.Add('--extra-instruction-path')
                $arguments.Add($extraInstructionForHarbor)
            }
        }
        $arguments.Add('--yes')
        return $arguments.ToArray()
    }

    function Invoke-HarborArm {
        param(
            [string]$Label,
            [string]$JobName,
            [string]$SkillPath
        )

        $arguments = New-HarborArguments $JobName $SkillPath
        Write-Host ""
        Write-Host "[$Label] harbor run $(Get-ArgumentDisplay $arguments)"
        if ($DryRun) {
            return
        }
        if ($useWsl) {
            & wsl.exe -d $WslDistribution --cd $repoForHarbor -- $harborExecutable run @arguments
        } else {
            & $harborExecutable run @arguments
        }
        if ($LASTEXITCODE -ne 0) {
            throw "Harbor $Label arm failed with exit code $LASTEXITCODE."
        }
    }

    Invoke-HarborArm 'no-skill' $jobNames.NoSkill $null
    Invoke-HarborArm 'previous' $jobNames.Previous $previousSkillForHarbor
    Invoke-HarborArm 'candidate' $jobNames.Candidate $candidateSkillForHarbor

    if ($DryRun) {
        Write-Host ""
        Write-Host "Dry run complete. Planned report: $reportHost"
        return
    }

    $summaryScript = Join-Path $PSScriptRoot 'summarize_harbor_comparison.py'
    $summaryArguments = [Collections.Generic.List[string]]::new()
    foreach ($value in @(
        $summaryScript,
        '--no-skill', (Join-Path (Join-Path $jobsDirHost $jobNames.NoSkill) 'result.json'),
        '--previous', (Join-Path (Join-Path $jobsDirHost $jobNames.Previous) 'result.json'),
        '--candidate', (Join-Path (Join-Path $jobsDirHost $jobNames.Candidate) 'result.json'),
        '--skill-name', $SkillName,
        '--task-name', $TaskName,
        '--previous-ref', $previousDescriptor,
        '--candidate-ref', $candidateDescriptor,
        '--task-ref', $taskDescriptor,
        '--agent', $Agent,
        '--model', $Model,
        '--attempts', $Attempts.ToString(),
        '--verified-reward-floor', $VerifiedRewardFloor.ToString([Globalization.CultureInfo]::InvariantCulture),
        '--output', $reportHost
    )) {
        $summaryArguments.Add($value)
    }
    if ($DashboardBaseUrl) {
        $summaryArguments.Add('--dashboard-base-url')
        $summaryArguments.Add($DashboardBaseUrl)
    }
    if ($FailOnRegression) {
        $summaryArguments.Add('--fail-on-regression')
    }

    & python @summaryArguments
    $summaryExitCode = $LASTEXITCODE
    if ($summaryExitCode -ne 0) {
        throw "Harbor comparison report failed with exit code $summaryExitCode."
    }
    Write-Host ""
    Write-Host "Comparison complete: $reportHost"
    Write-Host "View jobs: $DashboardBaseUrl"
} finally {
    [Environment]::SetEnvironmentVariable('HARBOR_TELEMETRY', $previousTelemetry, 'Process')
    [Environment]::SetEnvironmentVariable('PYTHONUTF8', $previousPythonUtf8, 'Process')
    if ($temporaryRoot) {
        $temporaryBase = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
        $resolvedTemporaryRoot = [IO.Path]::GetFullPath($temporaryRoot)
        if ($resolvedTemporaryRoot.StartsWith($temporaryBase, [StringComparison]::OrdinalIgnoreCase) -and
            (Split-Path -Leaf $resolvedTemporaryRoot).StartsWith('uxl-harbor-comparison-')) {
            Remove-Item -LiteralPath $resolvedTemporaryRoot -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            Write-Warning "Refusing to remove unexpected temporary path: $resolvedTemporaryRoot"
        }
    }
}
