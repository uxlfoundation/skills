[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Fa-f0-9]{40}$')]
    [string]$Thumbprint,

    [ValidateSet('CurrentUser', 'LocalMachine')]
    [string]$StoreLocation = 'CurrentUser',

    [ValidateSet('Process', 'User')]
    [string]$Scope = 'Process'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$normalizedThumbprint = $Thumbprint.ToUpperInvariant()
$certificatePath = "Cert:\$StoreLocation\Root\$normalizedThumbprint"
$certificate = Get-Item -LiteralPath $certificatePath

$derBase64 = [Convert]::ToBase64String($certificate.RawData)
$lines = for ($offset = 0; $offset -lt $derBase64.Length; $offset += 64) {
    $length = [Math]::Min(64, $derBase64.Length - $offset)
    $derBase64.Substring($offset, $length)
}
$pem = "-----BEGIN CERTIFICATE-----`n$($lines -join "`n")`n-----END CERTIFICATE-----`n"
$encodedPem = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pem))

$env:UXL_EXTRA_CA_CERT_B64 = $encodedPem
if ($Scope -eq 'User') {
    [Environment]::SetEnvironmentVariable(
        'UXL_EXTRA_CA_CERT_B64',
        $encodedPem,
        [EnvironmentVariableTarget]::User
    )
}

Write-Output "Configured public root certificate $normalizedThumbprint ($($certificate.Subject)) for $Scope-scoped UXL container builds."
