param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\..\output\maintainer-outreach-current")
)

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$source = Join-Path $repoRoot "evaluation\dashboard\public\decks"
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputDirectory)

if (-not $resolvedOutput.StartsWith($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "OutputDirectory must stay inside the repository."
}

New-Item -ItemType Directory -Path $resolvedOutput -Force | Out-Null
Get-ChildItem -LiteralPath $resolvedOutput -File -ErrorAction SilentlyContinue | Remove-Item -Force
Copy-Item -Path (Join-Path $source "*.pptx") -Destination $resolvedOutput
Copy-Item -Path (Join-Path $source "*.pdf") -Destination $resolvedOutput

$manifestPath = Join-Path $resolvedOutput "package-manifest.json"
$files = Get-ChildItem -LiteralPath $resolvedOutput -File |
    Where-Object { $_.Extension -in ".pptx", ".pdf" } |
    Sort-Object Name |
    ForEach-Object {
        [ordered]@{
            file = $_.Name
            bytes = $_.Length
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
[ordered]@{
    schemaVersion = "uxl-maintainer-deck-package.v1"
    generatedFor = "2026-09-04"
    files = @($files)
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding utf8

$zipPath = Join-Path $resolvedOutput "uxl-maintainer-outreach-decks.zip"
Compress-Archive -Path (Join-Path $resolvedOutput "*.pptx"), (Join-Path $resolvedOutput "*.pdf"), $manifestPath -DestinationPath $zipPath -Force
Write-Output $resolvedOutput
Write-Output $zipPath
