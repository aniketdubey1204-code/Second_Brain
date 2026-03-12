Set-Location 'D:\OpenClaw\workspace\second-brain'
# Check status
$status = git status --porcelain -uno
if (-not $status) { exit 0 }
# Changes exist
git add -A
$date = Get-Date -Format yyyy-MM-dd
git commit -m "Auto-sync: Daily changes $date" --quiet
if ($LASTEXITCODE -ne 0) { exit 1 }
# Try push
git push origin main --quiet
if ($LASTEXITCODE -ne 0) {
  git pull --rebase origin main --quiet
  git push origin main --quiet
  if ($LASTEXITCODE -ne 0) { exit 1 }
}
exit 0
