import json, re, sys, datetime, os, pathlib, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
import pathlib
sys.path.append(str(pathlib.Path(__file__).parents[3]))
import importlib.util, os, urllib.request, json

# Simple fetch of recent candles from Binance
def fetch_candles(symbol, interval='4h', limit=14):
    try:
        url = f'https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval={interval}&limit={limit}'
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
            return data  # each entry is a list, 4th index is close price
    except Exception:
        return []

# Calculate RSI (14 period) from candle data
def calc_rsi(candles, period=14):
    if not candles or len(candles) < period + 1:
        return None
    closes = [float(c[4]) for c in candles]
    gains = []
    losses = []
    for i in range(1, period+1):
        delta = closes[i] - closes[i-1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-delta)
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
sys.stdout.reconfigure(encoding='utf-8')

MEMORY_PATH = pathlib.Path('MEMORY.md')

def read_memory():
    if not MEMORY_PATH.exists():
        return ''
    return MEMORY_PATH.read_text(encoding='utf-8')

def parse_balance(text):
    m = re.search(r'Current virtual balance[:\s]*₹?\s*([\d,]+)', text, re.IGNORECASE)
    if m:
        return int(m.group(1).replace(',', ''))
    return 0

def parse_today_section(text):
    # Simple extraction of a section titled "## Daily Report" or similar not existent; fallback to empty
    return ''

def fetch_price(symbol):
    try:
        url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT'
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
            return float(data['price'])
    except Exception:
        return None

def fetch_rsi(symbol):
    # Placeholder: Binance does not provide RSI directly. Use last known from MEMORY if present
    return None

def main():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    mem = read_memory()
    balance = parse_balance(mem)
    # Dummy values for illustration
    pnl_amount = 0
    pnl_pct = 0
    open_positions = 0
    trades_table = 'No trades executed today.'
    total_trades = 0
    win_rate = 0
    max_dd = 0
    best_trade = 0
    worst_trade = 0
    streak = '0 wins'
    # Prices
    prices = {}
    for sym in ['BTC', 'ETH', 'SOL']:
        price = fetch_price(sym)
        if price is None:
            # fallback to last known price from MEMORY (search for a line)
            m = re.search(fr'{sym}.*price[:\s]*₹?\s*([\d.,]+)', mem)
            if m:
                price = float(m.group(1).replace(',', ''))
        prices[sym] = price
    # RSI placeholders using last known values in MEMORY (example regex)
    rsi_vals = {}
    for sym in ['BTC', 'ETH', 'SOL']:
        m = re.search(fr'{sym}.*RSI[:\s]*([\d.]+)', mem, re.IGNORECASE)
        if m:
            rsi_vals[sym] = float(m.group(1))
        else:
            rsi_vals[sym] = None
    def rsi_status(val):
        if val is None:
            return 'No data'
        if val < 35:
            return 'Approaching oversold - watch closely'
        if 35 <= val <= 50:
            return 'Neutral - no action'
        if 50 < val <= 65:
            return 'Neutral — no action'
        return 'Approaching overbought — watch closely'

    # Build watchlist using live RSI from trade_monitor
    watchlist_lines = []
    for sym in ['BTC','ETH','SOL']:
        candles = fetch_candles(sym, interval='4h', limit=14)
        rsi = calc_rsi(candles)
        if rsi is None:
            rsi_display = 'N/A'
            status = 'No data'
        else:
            rsi_display = f"{rsi:.2f}"
            if rsi < 35:
                status = '🔴 Approaching oversold — watch closely'
            elif rsi <= 50:
                status = '🟡 Neutral zone'
            elif rsi <= 65:
                status = '🟡 Neutral zone'
            else:
                status = '🔴 Approaching overbought — watch closely'
        watchlist_lines.append(f'- {sym} (RSI {rsi_display}): {status}')
    watchlist = '\n'.join(watchlist_lines)
    alerts = 'No alerts.'
    report = f"""📊 DAILY TRADING REPORT — {today}
━━━━━━━━━━━━━━━━━━━━━━
💼 Virtual Balance: ₹{balance}
📈 Today's P&L: +₹{pnl_amount} ({pnl_pct}%)
📂 Open Positions: {open_positions}
━━━━━━━━━━━━━━━━━━━━━━
📋 TODAY'S TRADES:
{trades_table}
━━━━━━━━━━━━━━━━━━━━━━
📊 OVERALL STATS:
- Total Trades: {total_trades}
- Win Rate: {win_rate}%
- Max Drawdown: {max_dd}%
- Best Trade: +₹{best_trade}
- Worst Trade: -₹{worst_trade}
- Current Streak: {streak}
━━━━━━━━━━━━━━━━━━━━━━
🔭 TOMORROW'S WATCHLIST:
{watchlist}
━━━━━━━━━━━━━━━━━━━━━━
⚠️ ALERTS: {alerts}
🟡 Mode: PAPER TRADING
━━━━━━━━━━━━━━━━━━━━━━
"""
    print(report)

if __name__ == '__main__':
    main()
