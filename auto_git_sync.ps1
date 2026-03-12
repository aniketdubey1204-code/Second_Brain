Set-Location "D:\OpenClaw\workspace\second-brain"
if (-not (Test-Path ".git")) {
    Write-Error "Repository not initialized."
    exit 1
}
$status = git status --porcelain -uno
if ($status) {
    git add -A
    $date = Get-Date -Format "yyyy-MM-dd"
    git commit -m "Auto-sync: Daily changes $date" --quiet
    git push origin main --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        git pull --rebase origin main --quiet
        git push origin main --quiet
    }
}
