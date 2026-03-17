import sys, json, time, datetime, os, requests
import pandas as pd

symbols = ['BTCUSDT','ETHUSDT','SOLUSDT']
now = int(time.time())
from_ts = now - 2*24*60*60  # 2 days ago

base = r'D:\\OpenClaw\\workspace\\second-brain\\agents\\trader'
balance_path = os.path.join(base, 'paper_balance.json')
positions_path = os.path.join(base, 'open_positions.json')

try:
    with open(balance_path) as f:
        balance_data = json.load(f)
        balance = balance_data.get('balance', 10000)
except Exception:
    balance = 10000

try:
    with open(positions_path) as f:
        positions = json.load(f)
except Exception:
    positions = []

max_positions = 3
if len(positions) >= max_positions:
    print(json.dumps({'action':'none','reason':'max positions reached'}))
    sys.exit()

risk_amount = 0.05 * balance
result = {'action':'none','reason':'no suitable trade'}

for sym in symbols:
    url = f'https://api.delta.exchange/v2/products/{sym}/candles'
    params = {'resolution':'15','from':from_ts,'limit':'200'}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        candles = data.get('result', [])
    except Exception:
        continue
    if len(candles) < 50:
        continue
    df = pd.DataFrame(candles)
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    delta = df['close'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(span=14, adjust=False).mean()
    roll_down = down.ewm(span=14, adjust=False).mean()
    rs = roll_up / roll_down
    df['rsi'] = 100 - (100 / (1 + rs))
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['mbb'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['upper'] = df['mbb'] + 2*df['std']
    df['lower'] = df['mbb'] - 2*df['std']
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    # Simple regime detection
    avg_width = (df['upper'] - df['lower']).mean()
    bb_width = latest['upper'] - latest['lower']
    if bb_width > 3 * avg_width:
        regime = 'C'
    else:
        if 45 <= latest['rsi'] <= 65 and latest['close'] > latest['ema20'] and latest['close'] > latest['ema50']:
            regime = 'A'
        else:
            regime = 'B'
    if regime == 'A':
        macd_cross = prev['macd'] < prev['macd_signal'] and latest['macd'] > latest['macd_signal']
        if macd_cross and 45 <= latest['rsi'] <= 65 and latest['close'] > latest['ema20'] and latest['close'] > latest['ema50']:
            entry = latest['close']
            sl = entry * 0.99
            tp = entry * 1.04
            qty = round(risk_amount / (entry - sl), 4) if entry>sl else 0
            result = {'action':'trade','symbol':sym,'side':'BUY','entry_price':entry,'stop_loss':sl,'take_profit':tp,'strategy':'A','regime':'A','quantity':qty}
            break
        macd_cross_down = prev['macd'] > prev['macd_signal'] and latest['macd'] < latest['macd_signal']
        if macd_cross_down and 35 <= latest['rsi'] <= 55 and latest['close'] < latest['ema20'] and latest['close'] < latest['ema50']:
            entry = latest['close']
            sl = entry * 1.01
            tp = entry * 0.96
            qty = round(risk_amount / (sl - entry), 4) if sl>entry else 0
            result = {'action':'trade','symbol':sym,'side':'SHORT','entry_price':entry,'stop_loss':sl,'take_profit':tp,'strategy':'A','regime':'A','quantity':qty}
            break
    elif regime == 'B':
        if latest['close'] <= latest['lower'] and latest['rsi'] < 35:
            entry = latest['close']
            sl = entry * 0.98
            tp = (latest['upper'] + latest['lower'])/2
            qty = round(risk_amount / (entry - sl), 4) if entry>sl else 0
            result = {'action':'trade','symbol':sym,'side':'BUY','entry_price':entry,'stop_loss':sl,'take_profit':tp,'strategy':'B','regime':'B','quantity':qty}
            break
        if latest['close'] >= latest['upper'] and latest['rsi'] > 65:
            entry = latest['close']
            sl = entry * 1.02
            tp = (latest['upper'] + latest['lower'])/2
            qty = round(risk_amount / (sl - entry), 4) if sl>entry else 0
            result = {'action':'trade','symbol':sym,'side':'SELL','entry_price':entry,'stop_loss':sl,'take_profit':tp,'strategy':'B','regime':'B','quantity':qty}
            break
    else:
        continue

print(json.dumps(result))
