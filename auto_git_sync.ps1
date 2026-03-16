cd D:\OpenClaw\workspace\second-brain
$changes = git status --porcelain
if (-not $changes) { exit 0 }
# Only stage daily journal and website files
git add brain-docs/daily public src
if ((git diff --cached --quiet) -or (git diff --cached --name-only | Measure-Object).Count -eq 0) { exit 0 }
git commit -m "Auto-sync: Daily changes $(Get-Date -Format yyyy-MM-dd)" --quiet
if ($LASTEXITCODE -ne 0) {
    git pull --rebase origin main --quiet
    git push origin main --quiet
} else {
    git push origin main --quiet
}