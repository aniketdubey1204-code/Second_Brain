# PowerShell risk monitor script
$base = "D:\OpenClaw\workspace\second-brain\agents\trader"
$positionsPath = Join-Path $base "open_positions.json"
$balancePath = Join-Path $base "paper_balance.json"

# Load JSON files
$positionsJson = Get-Content $positionsPath -Raw | ConvertFrom-Json
$balanceJson = Get-Content $balancePath -Raw | ConvertFrom-Json

$issues = @()

# Rule: max 3 positions
if ($positionsJson.positions.Count -gt 3) {
    $issues += "Too many open positions ($($positionsJson.positions.Count) > 3)."
}

# Rule: daily loss not exceed 5%
$initial = [double]$balanceJson.initial_capital
$current = [double]$balanceJson.current_balance
if ($initial -gt 0) {
    $lossPct = (1 - $current / $initial) * 100
    if ($lossPct -gt 5) {
        $issues += "Daily loss $([math]::Round($lossPct,2))% exceeds 5%."
    }
}

# Rule: each position must have a stopLoss defined (case‑insensitive field)
foreach ($pos in $positionsJson.positions) {
    if (-not $pos.PSObject.Properties.Name -contains "stopLoss" -or -not $pos.stopLoss) {
        $id = $pos.id
        $issues += "Position $id missing stop‑loss."
    }
}

# News check using Tavily (negative keywords)
$assets = @("BTC","ETH","SOL")
$negativeFound = $false
$tavilyScript = "D:\\OpenClaw\\workspace\\second-brain\\skills\\openclaw-tavily-search\\scripts\\tavily_search.py"
foreach ($asset in $assets) {
    $query = "$asset negative news OR crash OR black swan"
    $raw = python3 $tavilyScript --query "$query" --max-results 3 --format brave
    try {
        $json = $raw | ConvertFrom-Json
    } catch {
        continue
    }
    foreach ($res in $json.results) {
        if ($res.snippet -match "(?i)crash|down|drop|failure|black swan|regulation|bankruptcy|liquidation") {
            $negativeFound = $true
            $issues += "Negative news for ${asset}: $($res.title) $($res.url)"
        }
    }
}

if ($negativeFound) {
    $issues += "Negative market news detected - consider tightening all stop-losses."
}

if ($issues.Count -gt 0) {
    $summary = "Risk Monitor Alerts:`n" + ($issues -join "`n")
} else {
    $summary = "Risk Monitor: No issues detected."
}

Write-Output $summary
