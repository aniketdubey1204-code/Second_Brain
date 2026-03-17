$date = Get-Date -Format "yyyy-MM-dd"
$path = "D:\OpenClaw\workspace\second-brain\memory\$date.md"
if (-not (Test-Path $path)) {
    "# Daily Journal – $date`n`n- Auto-generated daily journal." | Set-Content -Path $path -Encoding UTF8
}
