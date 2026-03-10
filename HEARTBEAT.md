# HEARTBEAT.md
# Heartbeat checklist

## Git Auto-Sync Check (runs every 4 hours)
1. Check git status for uncommitted changes
2. If changes exist:
   - Stage all changes with `git add -A`
   - Commit with message: "Auto-sync: Daily changes $(date +%Y-%m-%d)"
   - Push to origin main
3. Report success or any issues

## Daily Journal Check
1. Check if today's memory file exists: memory/$(date +%Y-%m-%d).md
2. If missing, generate it with summary of activity

## Sub-Agent Status
1. Check for any stuck/failed sub-agent sessions
2. Relay any completed task results to user
