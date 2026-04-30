param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [string]$ExePath = "D:\ProgramData\PinganSec\TdxW.exe",
    [string]$TitleKey = "平安证券",
    [string]$Port = "COM3",
    [string]$OutputDir = "runtime\pingan-batch",
    [string]$SummaryPath = "runtime\pingan-batch-summary.json"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$singleScript = Join-Path $scriptDir "pingan-buy-turbo.ps1"
$resolvedInputPath = Resolve-Path $InputPath
$resolvedOutputDir = Join-Path $repoRoot $OutputDir
$resolvedSummaryPath = Join-Path $repoRoot $SummaryPath

if (-not (Test-Path $singleScript)) {
    throw "missing helper script: $singleScript"
}

New-Item -ItemType Directory -Force -Path $resolvedOutputDir | Out-Null

function Get-QueueItems {
    param([string]$Path)

    $ext = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($ext -eq ".json") {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($raw -is [System.Array]) {
            return $raw
        }
        if ($raw.orders) {
            return @($raw.orders)
        }
        throw "json queue must be an array or contain an 'orders' property"
    }
    if ($ext -eq ".csv") {
        return @(Import-Csv -LiteralPath $Path)
    }
    throw "unsupported queue format: $ext"
}

$items = @(Get-QueueItems -Path $resolvedInputPath)
$results = @()

for ($index = 0; $index -lt $items.Count; $index++) {
    $item = $items[$index]
    $code = [string]$item.code
    $price = [string]$item.price
    $quantity = [int]$item.quantity

    if ([string]::IsNullOrWhiteSpace($code) -or [string]::IsNullOrWhiteSpace($price) -or $quantity -le 0) {
        throw "invalid queue item at index $index: code=$code price=$price quantity=$quantity"
    }

    $orderId = if ($item.PSObject.Properties.Match("id").Count -gt 0 -and $item.id) { [string]$item.id } else { "{0:D3}" -f ($index + 1) }
    $outputPath = Join-Path $resolvedOutputDir ("order-{0}.json" -f $orderId)

    Write-Host ("[{0}/{1}] code={2} price={3} quantity={4}" -f ($index + 1), $items.Count, $code, $price, $quantity)

    $args = @(
        "-File", $singleScript,
        "-Code", $code,
        "-Price", $price,
        "-Quantity", $quantity,
        "-ExePath", $ExePath,
        "-TitleKey", $TitleKey,
        "-Port", $Port,
        "-Output", $outputPath
    )

    & powershell -NoProfile -ExecutionPolicy Bypass @args
    $exitCode = $LASTEXITCODE
    $resultRecord = [ordered]@{
        id = $orderId
        index = $index
        code = $code
        price = $price
        quantity = $quantity
        output_path = $outputPath
        exit_code = $exitCode
        ok = ($exitCode -eq 0)
    }
    $results += [pscustomobject]$resultRecord

    if ($exitCode -ne 0) {
        Write-Warning ("order {0} failed with exit code {1}" -f $orderId, $exitCode)
    }
}

$summary = [ordered]@{
    input_path = $resolvedInputPath
    output_dir = $resolvedOutputDir
    count = $items.Count
    results = $results
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resolvedSummaryPath -Encoding UTF8
Write-Host ("summary written to {0}" -f $resolvedSummaryPath)

