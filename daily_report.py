import json
import os
from datetime import datetime
from binance.client import Client

# Config - you may need API keys if required; use public endpoints for klines
API_KEY = os.getenv('BINANCE_API_KEY','')
API_SECRET = os.getenv('BINANCE_API_SECRET','')
client = Client(API_KEY, API_SECRET)

WATCHLIST = ['BTCUSDT','ETHUSDT','SOLUSDT']
INTERVAL = '4h'

def get_watchlist_rsi():
    """Return a dict of symbol->RSI (4H candles) using standard 14‑period RSI calculation."""
    rsi_dict = {}
    for sym in WATCHLIST:
        # fetch last 100 candles
        klines = client.get_klines(symbol=sym, interval=INTERVAL, limit=100)
        closes = [float(k[4]) for k in klines]
        # compute RSI 14
        period = 14
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
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_dict[sym] = round(rsi, 2)
    return rsi_dict

def read_virtual_balance():
    # MEMORY.md contains virtual balance line
    try:
        with open('MEMORY.md','r',encoding='utf-8') as f:
            for line in f:
                if 'Current virtual balance' in line:
                    # extract number after ₹
                    parts = line.split('₹')
                    if len(parts)>1:
                        bal = parts[1].split()[0].replace(',','')
                        return int(bal)
    except Exception:
        return None

def generate_report():
    rsi = get_watchlist_rsi()
    balance = read_virtual_balance() or 0
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    report = []
    report.append(f"📊 Daily Report – {now}")
    report.append(f"💰 Balance: ₹{balance}")
    report.append("🔎 RSI (4H):")
    for sym, val in rsi.items():
        report.append(f"- {sym[:-4]}: {val}")
    return "\n".join(report)

if __name__ == "__main__":
    txt = generate_report()
    # print(txt)  # suppressed for console compatibility
    # send to telegram via OpenClaw message tool
    # The caller will handle sending; we just output.
    # Optionally write to a temp file for later use.
    with open('daily_report_output.txt','w',encoding='utf-8') as f:
        f.write(txt)
