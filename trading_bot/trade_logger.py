"""Trade logger module.
Handles persisting trades to JSON and human‑readable markdown logs.
"""
import json
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

JSON_PATH = os.path.join(LOG_DIR, "trades.json")
MD_PATH = os.path.join(LOG_DIR, "TRADE_LOG.md")

def _load_json():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def log_trade(trade: dict):
    """Append a trade dict to both JSON and markdown logs.
    Expected keys: timestamp, symbol, side, entry_price, exit_price (optional),
    size, fee, pnl, reason.
    """
    # Ensure timestamp
    if 'timestamp' not in trade:
        trade['timestamp'] = datetime.utcnow().isoformat() + "Z"
    # JSON log
    data = _load_json()
    data.append(trade)
    _save_json(data)
    # Markdown log – simple line format
    line = f"- {trade['timestamp']} {trade['side'].upper()} {trade['size']} {trade['symbol']} @ ${trade['entry_price']:.2f}"
    if 'exit_price' in trade:
        line += f" → ${trade['exit_price']:.2f} (P&L: {trade.get('pnl',0):.2f})"
    line += f" – {trade.get('reason','')}\n"
    with open(MD_PATH, "a", encoding="utf-8") as f:
        f.write(line)
