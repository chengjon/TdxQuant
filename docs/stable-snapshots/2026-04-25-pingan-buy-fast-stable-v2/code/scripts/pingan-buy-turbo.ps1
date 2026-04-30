param(
    [Parameter(Mandatory = $true)]
    [string]$Code,

    [Parameter(Mandatory = $true)]
    [string]$Price,

    [Parameter(Mandatory = $true)]
    [int]$Quantity,

    [string]$ExePath = "D:\ProgramData\PinganSec\TdxW.exe",
    [string]$TitleKey = "平安证券",
    [string]$Port = "COM3",
    [string]$Output = "pingan-submit-once-result.json"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

Push-Location $repoRoot
try {
    python -m tdxquant.cli `
        --exe-path $ExePath `
        --title-key $TitleKey `
        pingan-buy `
        --port $Port `
        --profile turbo `
        --code $Code `
        --price $Price `
        --quantity $Quantity `
        --output $Output
}
finally {
    Pop-Location
}
