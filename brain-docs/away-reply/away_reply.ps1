# away_reply.ps1 – Auto-reply script for WhatsApp when /away on
# Checks flag file, polls for new WhatsApp messages, generates dynamic replies via a sub‑agent, and sends them back.

$flagPath = "D:\OpenClaw\workspace\second-brain\brain-docs\away-mode.txt"
$lastIdFile = "D:\OpenClaw\workspace\second-brain\brain-docs\away-reply\last_msg_id.txt"

function Get-LastProcessedId {
    if (Test-Path $lastIdFile) { Get-Content $lastIdFile -Raw } else { '' }
}

function Set-LastProcessedId($id) {
    Set-Content -Path $lastIdFile -Value $id -Encoding UTF8
}

while ($true) {
    # Read flag – only proceed if it's "on"
    if ((Get-Content $flagPath -Raw).Trim().ToLower() -eq 'on') {
        # Pull new messages (JSON) from WhatsApp using OpenClaw CLI (poll once)
        $messagesJson = & openclaw whatsapp poll --channel whatsapp --output json --since (Get-Date).AddSeconds(-30) 2>$null
        if ($messagesJson) {
            $messages = $messagesJson | ConvertFrom-Json
            foreach ($msg in $messages) {
                $msgId = $msg.id
                $lastId = Get-LastProcessedId
                if ($msgId -le $lastId) { continue }
                $text = $msg.text
                # Spawn a sub‑agent to generate a reply (using Haiku model for speed)
                $reply = & openclaw sessions_spawn --task "reply-to-msg" --runtime acp --model haiku --message $text --timeoutSeconds 30 --runTimeoutSeconds 30 | Out-String
                # Send the reply back via WhatsApp
                & openclaw message send --channel whatsapp --target $msgId --message $reply.Trim()
                Set-LastProcessedId $msgId
            }
        }
    }
    Start-Sleep -Seconds 20
}
