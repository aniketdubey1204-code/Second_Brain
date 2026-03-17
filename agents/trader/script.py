import requests, json, statistics

def fetch_candles(symbol, interval='15m', limit=200):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    r = requests.get(url)
    data = r.json()
    ohlc = [(float(d[1]), float(d[2]), float(d[3]), float(d[4]), float(d[5])) for d in data]
    return ohlc

def ema(prices, period):
    k = 2/(period+1)
    ema_val = prices[0]
    for price in prices[1:]:
        ema_val = price * k + ema_val * (1 - k)
    return ema_val

def rsi(closes, period=14):
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
    if len(gains) < period:
        return None
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def bollinger(closes, period=20, std_mult=2):
    if len(closes) < period:
        return None, None, None
    recent = closes[-period:]
    sma = sum(recent) / period
    std = statistics.stdev(recent)
    upper = sma + std_mult * std
    lower = sma - std_mult * std
    width = upper - lower
    return upper, lower, width

def avg_volume(volumes, period=20):
    if len(volumes) < period:
        return None
    return sum(volumes[-period:]) / period

symbols = ['BTCUSDT','ETHUSDT','SOLUSDT']
results = {}
for sym in symbols:
    candles = fetch_candles(sym)
    closes = [c[3] for c in candles]
    volumes = [c[4] for c in candles]
    last_close = closes[-1]
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    rsi14 = rsi(closes)
    bb_up, bb_low, bb_width = bollinger(closes)
    avg_vol = avg_volume(volumes)
    vol_spike = volumes[-1] > (2 * avg_vol if avg_vol else 0)
    results[sym] = {
        'price': last_close,
        'ema20': ema20,
        'ema50': ema50,
        'rsi': rsi14,
        'bb_width': bb_width,
        'vol_spike': vol_spike,
    }
print(json.dumps(results))
