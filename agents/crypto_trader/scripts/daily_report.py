import json, os, sys, datetime, requests

# Helpers
def load_memory():
    mem_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../MEMORY.md'))
    if not os.path.exists(mem_path):
        return ''
    with open(mem_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_section(text, header):
    # Simple split by header lines starting with ##
    sections = text.split('##')
    for sec in sections:
        if sec.strip().startswith(header):
            return sec.strip().split('\n')[1:]
    return []

def get_today_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_virtual_balance(mem):
    # Expect a line like "Virtual Balance: ₹12345" in MEMORY.md
    for line in mem.splitlines():
        if 'Virtual Balance' in line:
            parts = line.split('₹')
            if len(parts) > 1:
                try:
                    return float(parts[1].replace(',', '').strip())
                except:
                    pass
    return 0.0

def get_trades_today(mem):
    date = get_today_date()
    # Look for a section titled "Trades {date}" or similar. For simplicity, find lines with the date.
    trades = []
    for line in mem.splitlines():
        if date in line and ('P&L' in line or 'Entry' in line):
            trades.append(line)
    return trades

def fetch_price(symbol):
    try:
        resp = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT', timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return float(data['price'])
    except Exception as e:
        return None

def fetch_rsi(symbol):
    # Simple RSI via Binance klines (14 period) – approximate.
    try:
        endpoint = f'https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1d&limit=15'
        resp = requests.get(endpoint, timeout=5)
        resp.raise_for_status()
        klines = resp.json()
        closes = [float(k[4]) for k in klines]
        if len(closes) < 15:
            return None
        gains = []
        losses = []
        for i in range(1, len(closes)):
            delta = closes[i] - closes[i-1]
            if delta > 0:
                gains.append(delta)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-delta)
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 1)
    except Exception:
        return None

def format_trade_table(trades):
    # Expect trades as list of dicts; for now placeholder.
    if not trades:
        return "No trades executed today."
    header = "| Pair | Direction | Entry | Exit/Current | P&L | Status |"
    rows = [header]
    for t in trades:
        rows.append(f"| {t.get('pair','-')} | {t.get('direction','-')} | {t.get('entry','-')} | {t.get('exit','-')} | {t.get('pnl','-')} | {t.get('status','-')} |")
    return "\n".join(rows)

def main():
    mem = load_memory()
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    balance = get_virtual_balance(mem)
    # For demo, compute P&L and open count as zeros.
    todays_pnl = 0.0
    pnl_percent = 0.0
    open_positions = 0
    # Trades parsing (very naive)
    trades = []  # List of dicts for table
    # Attempt to fetch prices
    prices = {}
    for sym in ['BTC', 'ETH', 'SOL']:
        price = fetch_price(sym)
        if price is None:
            # fallback from memory – look for a line like "BTC price: $xxxx"
            price = None
            for line in mem.splitlines():
                if f"{sym} price" in line:
                    try:
                        price = float(line.split('$')[-1].strip())
                    except:
                        pass
            if price is None:
                price = 0.0
        prices[sym] = price
    # RSI
    rsi_vals = {}
    for sym in ['BTC', 'ETH', 'SOL']:
        rsi = fetch_rsi(sym)
        if rsi is None:
            # fallback from memory
            rsi = 0
        rsi_vals[sym] = rsi
    # Stats placeholders
    total_trades = 0
    win_rate = 0
    max_drawdown = 0
    best_trade = 0
    worst_trade = 0
    streak = "0 wins"
    # Alerts placeholder
    alerts = []
    # Build output
    output = f"📊 DAILY TRADING REPORT — {date_str}\n" + "━━━━━━━━━━━━━━━━━━━━━━\n"
    output += f"💼 Virtual Balance: ₹{balance:,.2f}\n"
    sign = '+' if todays_pnl >= 0 else '-'
    output += f"📈 Today's P&L: {sign}₹{abs(todays_pnl):,.2f} ({sign}{abs(pnl_percent):.2f}%)\n"
    output += f"📂 Open Positions: {open_positions}\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━\n"
    output += "📋 TODAY'S TRADES:\n"
    output += format_trade_table(trades) + "\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━\n"
    output += "📊 OVERALL STATS:\n"
    output += f"• Total Trades: {total_trades}\n"
    output += f"• Win Rate: {win_rate}%\n"
    output += f"• Max Drawdown: {max_drawdown}%\n"
    output += f"• Best Trade: +₹{best_trade}\n"
    output += f"• Worst Trade: -₹{worst_trade}\n"
    output += f"• Current Streak: {streak}\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━\n"
    output += "🔭 TOMORROW'S WATCHLIST:\n"
    for sym in ['BTC', 'ETH', 'SOL']:
        rsi = rsi_vals[sym]
        if rsi < 35:
            status = "Approaching oversold — watch closely"
        elif rsi > 65:
            status = "Approaching overbought — watch closely"
        else:
            status = "Neutral — no action"
        output += f"• {sym} (RSI {rsi}): {status}\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━\n"
    output += "⚠️ ALERTS: "
    if alerts:
        output += ", ".join(alerts)
    else:
        output += "No alerts."
    output += "\nMode: PAPER TRADING 🟡\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━"
    sys.stdout.buffer.write(output.encode('utf-8'))

if __name__ == '__main__':
    main()
