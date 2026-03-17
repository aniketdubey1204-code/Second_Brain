import sys, json, urllib.request, pandas as pd, numpy as np, datetime, os

# Config
symbols = ['BTC','ETH','SOL']
vs_currency = 'usd'
# fetch last 100 15min candles via CoinGecko OHLC endpoint (requires days param, use 1 day gives hourly; we need 15min maybe not available). Use market_chart endpoint for 1 day minute data.

def fetch_data(symbol):
    # Map symbol to Binance symbol format
    binance_symbol = symbol.upper().replace('_', '') + 'USDT' if not symbol.lower().endswith('usdt') else symbol.upper()
    # Use Binance public klines endpoint (15m interval, 200 candles)
    url = f'https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval=15m&limit=200'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    # data is list of [Open time, Open, High, Low, Close, Volume, Close time, ...]
    df = pd.DataFrame(data, columns=['open_time','open','high','low','close','volume','close_time','quote_asset_volume','num_trades','taker_buy_base_asset_volume','taker_buy_quote_asset_volume','ignore'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)
    df['price'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df[['price','volume']]

def compute_indicators(df):
    # EMA
    df['EMA20'] = df['price'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['price'].ewm(span=50, adjust=False).mean()
    # RSI
    delta = df['price'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / roll_down
    df['RSI'] = 100 - (100 / (1 + rs))
    # Bollinger Bands
    df['BB_Middle'] = df['price'].rolling(20).mean()
    df['BB_Std'] = df['price'].rolling(20).std()
    df['BB_Upper'] = df['BB_Middle'] + 2 * df['BB_Std']
    df['BB_Lower'] = df['BB_Middle'] - 2 * df['BB_Std']
    # Placeholder ADX (use RSI derivative as proxy) – set to 30 for trending detection
    df['ADX'] = 30
    return df

def detect_regime(df):
    latest = df.iloc[-1]
    adx = latest['ADX']
    price = latest['price']
    # price HH/LL detection using last 5 periods
    recent = df.tail(5)
    high_high = recent['price'].max()
    low_low = recent['price'].min()
    is_hh = price >= high_high
    is_ll = price <= low_low
    # Bollinger width
    bb_width = latest['BB_Upper'] - latest['BB_Lower']
    # average width of last 20 periods
    avg_width = df['BB_Upper'].sub(df['BB_Lower']).rolling(20).mean().iloc[-1]
    vol_spike = False  # placeholder, volume not available via coingecko
    if adx and adx > 25 and (is_hh or is_ll):
        return 'A'
    if adx and adx < 20 and (price <= latest['BB_Upper'] and price >= latest['BB_Lower']):
        return 'B'
    if avg_width and bb_width > 3 * avg_width:
        return 'C'
    return 'Unknown'

def strategy_a_signal(df):
    latest = df.iloc[-1]
    # MACD bullish crossover: macd line crosses above signal line
    ema12 = df['price'].ewm(span=12, adjust=False).mean()
    ema26 = df['price'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_prev = macd.shift(1)
    signal_prev = signal.shift(1)
    bullish = (macd > signal) & (macd_prev <= signal_prev)
    bearish = (macd < signal) & (macd_prev >= signal_prev)
    rsi = latest['RSI']
    price = latest['price']
    cond_buy = bullish.iloc[-1] and 45 <= rsi <= 65 and price > latest['EMA20'] and price > latest['EMA50']
    cond_sell = bearish.iloc[-1] and 35 <= rsi <= 55 and price < latest['EMA20'] and price < latest['EMA50']
    return ('BUY' if cond_buy else None) if cond_buy else ('SELL' if cond_sell else None)

def strategy_b_signal(df):
    latest = df.iloc[-1]
    price = latest['price']
    rsi = latest['RSI']
    # Stoch RSI placeholder not computed
    # Use Bollinger positions
    if price <= latest['BB_Lower'] and rsi < 35:
        return 'BUY'
    if price >= latest['BB_Upper'] and rsi > 65:
        return 'SELL'
    return None

# Load existing data
balance_path = os.path.join(os.path.dirname(__file__), 'paper_balance.json')
positions_path = os.path.join(os.path.dirname(__file__), 'open_positions.json')
trades_log_path = os.path.join(os.path.dirname(__file__), 'trades.log')

if os.path.exists(balance_path):
    with open(balance_path) as f:
        balance = json.load(f)
else:
    balance = {'balance':10000}

if os.path.exists(positions_path):
    with open(positions_path) as f:
        data = json.load(f)
        positions = data.get('positions', [])
else:
    positions = []

summary = []

for sym in symbols:
    df = fetch_data(sym)
    df = compute_indicators(df)
    regime = detect_regime(df)
    summary.append(f"{sym.upper()} regime: {regime}")
    # Skip if Regime C for new trades
    if regime == 'C':
        # protect existing positions for this symbol
        for pos in positions:
            if pos['symbol'].lower() == sym:
                # tighten SL to 0.5% from entry
                if pos['side'] == 'long':
                    pos['stop_loss'] = round(pos['entry'] * 0.995, 2)
                else:
                    pos['stop_loss'] = round(pos['entry'] * 1.005, 2)
                summary.append(f"Protected position {pos['id']} for {sym.upper()} with tighter SL {pos['stop_loss']}")
        continue
    # Check existing open position limit
    open_cnt = len([p for p in positions if p['symbol'].lower() == sym])
    if open_cnt >= 1:
        summary.append(f"Already open position for {sym.upper()}, skipping new entry.")
        continue
    if len(positions) >= 3:
        summary.append("Max open positions reached, cannot open new trade.")
        break
    # Determine signal based on regime
    signal = None
    if regime == 'A':
        signal = strategy_a_signal(df)
    elif regime == 'B':
        signal = strategy_b_signal(df)
    if not signal:
        summary.append(f"No signal for {sym.upper()} under regime {regime}.")
        continue
    # Simulate trade
    price = df['price'].iloc[-1]
    # simple risk: 5% of balance
    risk_amount = balance['balance'] * 0.05
    # placeholder SL and TP
    if signal == 'BUY':
        sl = price * 0.98  # 2% stop loss
        tp = price * 1.04  # 4% TP
    else:
        sl = price * 1.02
        tp = price * 0.96
    # compute quantity
    qty = risk_amount / abs(price - sl)
    qty = round(qty, 4)
    # Update balance (simulate entry cost)
    balance['balance'] -= risk_amount
    # Record position
    pos = {
        'id': len(positions)+1,
        'symbol': sym.upper(),
        'side': 'long' if signal=='BUY' else 'short',
        'entry': round(price,2),
        'stop_loss': round(sl,2),
        'target': round(tp,2),
        'quantity': qty,
        'strategy': 'A' if regime=='A' else 'B',
        'regime': regime,
        'timestamp': datetime.datetime.now().isoformat()
    }
    positions.append(pos)
    # Log trade
    log_line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST] | {sym.upper()} | {pos['strategy']} | {regime} | Entry: {pos['entry']} | Exit: - | P&L: - | Reason In: {signal} | Reason Out: - | What went right: - | What went wrong: - | Lesson: -"
    with open(trades_log_path, 'a') as f:
        f.write(log_line + '\n')
    summary.append(f"Opened {signal} trade for {sym.upper()} at {price:.2f}, qty {qty}, SL {sl:.2f}, TP {tp:.2f}")

# Save files
with open(balance_path, 'w') as f:
    json.dump(balance, f, indent=2)
with open(positions_path, 'w') as f:
    json.dump({'positions': positions, 'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M %Z')}, f, indent=2)

print('\n'.join(summary))
