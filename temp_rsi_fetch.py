import os, json, urllib.request
from binance import Client
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
for sym in ['BTC','ETH','SOL']:
    klines = client.get_klines(symbol=sym+'USDT', interval='4h', limit=50)
    closes = [float(c[4]) for c in klines]
    period = 14
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
    avg_gain = sum(gains)/period
    avg_loss = sum(losses)/period
    rs = avg_gain/avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100/(1+rs)) if avg_loss != 0 else 100
    print(sym, round(rsi,2))
