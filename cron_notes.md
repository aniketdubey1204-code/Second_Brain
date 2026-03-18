# Cron Updates

- **daily-journal-generator**: Updated to generate daily journal files in the `daily/` folder instead of `memory/`.
- Ensure that the script invoked by this cron writes to `daily/$(Get-Date -Format yyyy-MM-dd).md`.
