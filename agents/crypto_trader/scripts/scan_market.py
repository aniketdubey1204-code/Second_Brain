import os, json, requests, pandas as pd
from datetime import datetime, timezone, timedelta

def fetch(symbol):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=4h&limit=200'
    r = requests.get(url, timeout=10)
    data = r.json()
    df = pd.DataFrame(data, columns=['open_time','open','high','low','close','volume','close_time','quote_asset_volume','num_trades','taker_buy_base_vol','taker_buy_quote_vol','ignore'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    return df

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.ewm(com=period-1, adjust=False).mean()
    ma_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ma_up/ma_down
    return 100 - (100/(1+rs))

def macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line.iloc[-1], signal_line.iloc[-1], hist.iloc[-1]

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean().iloc[-1]

pairs = ['BTCUSDT','ETHUSDT','SOLUSDT']
results = {}
for p in pairs:
    df = fetch(p)
    df['rsi'] = rsi(df['close'])
    macd_val, macd_sig, macd_hist = macd(df['close'])
    vol_avg = df['volume'].rolling(20).mean().iloc[-1]
    vol_curr = df['volume'].iloc[-1]
    vol_pct = (vol_curr - vol_avg)/vol_avg * 100 if vol_avg else 0
    ema20 = ema(df['close'], 20)
    ema50 = ema(df['close'], 50)
    results[p] = {
        'rsi': round(df['rsi'].iloc[-1],2),
        'macd_cross': 'bullish' if macd_hist>0 else ('bearish' if macd_hist<0 else 'none'),
        'volume_pct': round(vol_pct,2),
        'ema20_gt_ema50': str(ema20>ema50),
        'ema20': round(ema20,2),
        'ema50': round(ema50,2)
    }
print(json.dumps(results))
