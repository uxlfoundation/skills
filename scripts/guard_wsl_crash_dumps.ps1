#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$SentinelPath,

    [string]$CrashDumpDirectory = (Join-Path ([IO.Path]::GetTempPath()) 'wsl-crashes'),

    [ValidateRange(100, 10000)]
    [int]$PollMilliseconds = 250
)

$ErrorActionPreference = 'Stop'
$temporaryRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
$resolvedSentinel = [IO.Path]::GetFullPath($SentinelPath)
$resolvedCrashDumpDirectory = [IO.Path]::GetFullPath($CrashDumpDirectory)

foreach ($path in @($resolvedSentinel, $resolvedCrashDumpDirectory)) {
    if (-not $path.StartsWith($temporaryRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Crash-dump guard paths must stay under the user temporary directory: $path"
    }
}

$startedAt = [DateTime]::UtcNow

function Clear-NewWslCrashDumps {
    if (-not (Test-Path -LiteralPath $resolvedCrashDumpDirectory -PathType Container)) {
        return
    }

    foreach ($dump in Get-ChildItem -LiteralPath $resolvedCrashDumpDirectory -Filter 'wsl-crash-*.dmp' -File -ErrorAction SilentlyContinue) {
        if ($dump.LastWriteTimeUtc -lt $startedAt -or $dump.Length -eq 0) {
            continue
        }

        try {
            $stream = [IO.File]::Open($dump.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
            try {
                $stream.SetLength(0)
            } finally {
                $stream.Dispose()
            }
        } catch [IO.IOException] {
            # WSL may still be writing the dump. The next poll retries it.
        } catch [UnauthorizedAccessException] {
            # A transient access failure is retried while the sentinel exists.
        }
    }
}

while (Test-Path -LiteralPath $resolvedSentinel -PathType Leaf) {
    Clear-NewWslCrashDumps
    Start-Sleep -Milliseconds $PollMilliseconds
}

Clear-NewWslCrashDumps
