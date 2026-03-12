cd D:\OpenClaw\workspace\second-brain
$changes = git status --porcelain
if (-not $changes) { exit 0 }
git add -A
git commit -m "Auto-sync: Daily changes $(Get-Date -Format yyyy-MM-dd)" --quiet
if ($LASTEXITCODE -ne 0) {
    git pull --rebase origin main --quiet
    git push origin main --quiet
} else {
    git push origin main --quiet
}