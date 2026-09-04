param(
    [string]$DeckDirectory = (Join-Path $PSScriptRoot "..\..\evaluation\dashboard\public\decks")
)

$resolvedDeckDirectory = (Resolve-Path -LiteralPath $DeckDirectory).Path
$powerPoint = New-Object -ComObject PowerPoint.Application

try {
    Get-ChildItem -LiteralPath $resolvedDeckDirectory -Filter "*.pptx" | ForEach-Object {
        $presentation = $powerPoint.Presentations.Open($_.FullName, $true, $false, $false)
        try {
            $pdfPath = [System.IO.Path]::ChangeExtension($_.FullName, ".pdf")
            if (Test-Path -LiteralPath $pdfPath) {
                Remove-Item -LiteralPath $pdfPath -Force
            }
            $presentation.SaveAs($pdfPath, 32)
            Write-Output $pdfPath
        }
        finally {
            $presentation.Close()
        }
    }
}
finally {
    $powerPoint.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint) | Out-Null
}
