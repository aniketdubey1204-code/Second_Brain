#!/usr/bin/env python3
import json, subprocess, os, datetime, sys
import requests

# Fetch live prices from Delta Exchange API for BTC, ETH, SOL
API_URL = "https://api.delta.exchange/v2/tickers?symbol=BTC-USD,ETH-USD,SOL-USD"
try:
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    prices = {}
    # The response format includes a list under 'result'
    for item in data.get('result', []):
        symbol = item.get('symbol')
        if symbol:
            # Normalize to just the asset name (BTC, ETH, SOL)
            asset = symbol.split('-')[0]
            # Use 'last_price' if available, otherwise 'mark_price'
            price = item.get('last_price') or item.get('mark_price')
            if price:
                prices[asset] = price
except Exception as e:
    print(f"Failed to fetch prices: {e}", file=sys.stderr)
    sys.exit(1)

# Run Tavily search for latest crypto news (Markdown format)
TAVILY_SCRIPT = os.path.expanduser("~/OpenClaw/workspace/second-brain/skills/openclaw-tavily-search/scripts/tavily_search.py")
try:
    result = subprocess.run([
        "python3", TAVILY_SCRIPT,
        "--query", "latest crypto news",
        "--max-results", "5",
        "--format", "md"
    ], capture_output=True, text=True, check=True)
    news_md = result.stdout.strip()
except Exception as e:
    news_md = f"Failed to fetch news: {e}"

# Simple market regime detection – placeholder logic
# If BTC price > 75000 USD and ETH price > 2500 USD, consider "bullish"
btc_price = prices.get('BTC', 0)
eth_price = prices.get('ETH', 0)
sol_price = prices.get('SOL', 0)

regime = "neutral"
if btc_price > 75000 and eth_price > 2500:
    regime = "bullish"
elif btc_price < 70000 and eth_price < 2000:
    regime = "bearish"

# If regime is bullish, execute a dummy paper trade for BTC
trade_executed = False
trade_detail = {}
if regime == "bullish":
    # Dummy trade: buy 0.01 BTC at current price
    qty = 0.01
    trade_detail = {
        "time": datetime.datetime.utcnow().isoformat() + "Z",
        "symbol": "BTC",
        "side": "buy",
        "quantity": qty,
        "price": btc_price,
        "note": "paper trade from market scan"
    }
    trade_executed = True
    # Append to trades.log
    log_path = os.path.join(os.path.dirname(__file__), "trades.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(trade_detail) + "\n")
    # Update open_positions.json (simple list of positions)
    pos_path = os.path.join(os.path.dirname(__file__), "open_positions.json")
    positions = []
    if os.path.exists(pos_path):
        with open(pos_path, "r", encoding="utf-8") as f:
            try:
                positions = json.load(f)
            except Exception:
                positions = []
    # Add position (average price, quantity)
    positions.append({
        "symbol": "BTC",
        "quantity": qty,
        "avg_price": btc_price,
        "opened_at": trade_detail["time"]
    })
    with open(pos_path, "w", encoding="utf-8") as f:
        json.dump(positions, f, indent=2)

# Summarize the scan
summary = {
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "prices": prices,
    "regime": regime,
    "news": news_md,
    "trade_executed": trade_executed,
    "trade_detail": trade_detail if trade_executed else None
}
print(json.dumps(summary, indent=2))
