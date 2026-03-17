import requests, time, json, math, sys
from datetime import datetime, timedelta

# Config
symbols = ['BTCUSD', 'ETHUSD', 'SOLUSD']
base_url = 'https://api.india.delta.exchange/v2'
resolution = 15 * 60  # seconds for 15-min candles

def get_product_id(symbol):
    # Fetch all products and find matching symbol
    url = f"{base_url}/products"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    for p in data.get('result', []):
        if p.get('symbol') == symbol:
            return p.get('id')
    raise ValueError(f"Product ID not found for symbol {symbol}")

def fetch_candles(symbol, limit=200):
    product_id = get_product_id(symbol)
    to_ts = int(time.time())
    from_ts = to_ts - limit * resolution
    url = f"{base_url}/products/{product_id}/candles?resolution={resolution}&from={from_ts}&to={to_ts}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    candles = data.get('result', [])
    return candles

def ema(values, period):
    k = 2 / (period + 1)
    ema_vals = []
    for i, price in enumerate(values):
        if i == 0:
            ema_vals.append(price)
        else:
            ema_vals.append(price * k + ema_vals[-1] * (1 - k))
    return ema_vals

def sma(values, period):
    sma_vals = []
    for i in range(len(values)):
        if i + 1 < period:
            sma_vals.append(None)
        else:
            sma_vals.append(sum(values[i+1-period:i+1]) / period)
    return sma_vals

def rsi(prices, period=14):
    gains = []
    losses = []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi_vals = [None] * (period)
    rsi_vals.append(100 - 100 / (1 + rs) if avg_loss != 0 else 100)
    for i in range(period+1, len(prices)):
        gain = gains[i-1]
        loss = losses[i-1]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi_vals.append(100 - 100 / (1 + rs) if avg_loss != 0 else 100)
    return rsi_vals

def macd(prices, fast=12, slow=26, signal=9):
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_line = ema(macd_line, signal)
    histogram = [m - s for m, s in zip(macd_line, signal_line)]
    return macd_line, signal_line, histogram

def adx(highs, lows, closes, period=14):
    tr_list = []
    plus_dm = []
    minus_dm = []
    for i in range(1, len(closes)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        tr_list.append(tr)
        up_move = highs[i] - highs[i-1]
        down_move = lows[i-1] - lows[i]
        plus = up_move if up_move > down_move and up_move > 0 else 0
        minus = down_move if down_move > up_move and down_move > 0 else 0
        plus_dm.append(plus)
        minus_dm.append(minus)
    # Smooth averages
    atr = sum(tr_list[:period]) / period
    plus_di = sum(plus_dm[:period]) / period
    minus_di = sum(minus_dm[:period]) / period
    adx_vals = []
    for i in range(period, len(tr_list)):
        atr = (atr * (period - 1) + tr_list[i]) / period
        plus_di = (plus_di * (period - 1) + plus_dm[i]) / period
        minus_di = (minus_di * (period - 1) + minus_dm[i]) / period
        if atr == 0:
            dx = 0
        else:
            di_diff = abs(plus_di - minus_di)
            di_sum = plus_di + minus_di
            dx = (di_diff / di_sum) * 100 if di_sum != 0 else 0
        if len(adx_vals) == 0:
            adx_vals.append(dx)
        else:
            adx_vals.append((adx_vals[-1] * (period - 1) + dx) / period)
    return adx_vals[-1] if adx_vals else 0

def bollinger_bands(prices, period=20, std_mult=2):
    sb = sma(prices, period)
    bands = []
    for i in range(len(prices)):
        if i+1 < period:
            bands.append((None, None, None))
        else:
            ma = sb[i]
            window = prices[i+1-period:i+1]
            std = (sum((p - ma) ** 2 for p in window) / period) ** 0.5
            bands.append((ma - std_mult * std, ma, ma + std_mult * std))
    return bands

def volume_average(volumes, period=10):
    avgs = []
    for i in range(len(volumes)):
        if i+1 < period:
            avgs.append(None)
        else:
            avgs.append(sum(volumes[i+1-period:i+1]) / period)
    return avgs

def detect_regime(adx_val, bb_width, volume_spike, vol_avg):
    # Regime C: BB width > 3x normal OR volume spike >200%
    if bb_width > 3 * (bb_width / 2):  # placeholder, not accurate
        return 'C'
    if volume_spike > 2.0:
        return 'C'
    if adx_val > 25:
        return 'A'
    if adx_val < 20:
        return 'B'
    return 'B'

def main():
    signals = []
    for sym in symbols:
        try:
            candles = fetch_candles(sym, limit=200)
        except Exception as e:
            print(f'Error fetching candles for {sym}: {e}', file=sys.stderr)
            candles = []
        if len(candles) < 50:
            # Not enough data, try fallback to coingecko price
            try:
                cg_map = {'BTCUSD':'bitcoin','ETHUSD':'ethereum','SOLUSD':'solana','BTCUSDT':'bitcoin','ETHUSDT':'ethereum','SOLUSDT':'solana'}
                cg_id = cg_map.get(sym)
                if cg_id:
                    resp = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd")
                    resp.raise_for_status()
                    data = resp.json()
                    price = data.get(cg_id, {}).get('usd')
                    if price:
                        signals.append({
                            'symbol': sym,
                            'direction': 'LONG',
                            'strategy': 'fallback',
                            'regime': 'N/A',
                            'price': price
                        })
            except Exception:
                pass
            continue
        closes = [c['c'] for c in candles]
        opens = [c['o'] for c in candles]
        highs = [c['h'] for c in candles]
        lows = [c['l'] for c in candles]
        volumes = [c['v'] for c in candles]
        # indicators
        ema20 = ema(closes, 20)
        ema50 = ema(closes, 50)
        rsi_vals = rsi(closes)
        macd_line, signal_line, hist = macd(closes)
        adx_val = adx(highs, lows, closes)
        bb = bollinger_bands(closes)
        # latest values
        # Determine price and log endpoint used
        price = closes[-1]
        endpoint = "Delta Exchange (candles)"
        # SOL price sanity check – if price seems off (< $10) use CoinGecko fallback
        if sym == 'SOLUSD' and price < 10:
            # Fallback to CoinGecko
            try:
                cg_map = {'SOLUSD': 'solana'}
                cg_id = cg_map.get(sym)
                resp = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd", timeout=10)
                resp.raise_for_status()
                data = resp.json()
                price = data.get(cg_id, {}).get('usd')
                endpoint = "CoinGecko"
                # Log fallback usage
                print(f'Fallback to CoinGecko for {sym}, price={price}', file=sys.stderr)
            except Exception as e:
                print(f'Error fetching fallback price for {sym}: {e}', file=sys.stderr)
        # SOL price sanity check – if price seems off (< $10) use CoinGecko fallback
        if sym == 'SOLUSD' and price < 10:
            # Fallback to CoinGecko
            try:
                cg_map = {'SOLUSD': 'solana'}
                cg_id = cg_map.get(sym)
                resp = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd", timeout=10)
                resp.raise_for_status()
                data = resp.json()
                price = data.get(cg_id, {}).get('usd')
                # Log fallback usage
                print(f'Fallback to CoinGecko for {sym}, price={price}', file=sys.stderr)
            except Exception as e:
                print(f'Error fetching fallback price for {sym}: {e}', file=sys.stderr)

        ema20_cur = ema20[-1]
        ema50_cur = ema50[-1]
        rsi_cur = rsi_vals[-1]
        macd_cur = macd_line[-1]
        macd_prev = macd_line[-2]
        # Detect regime simplistic
        bb_mid = bb[-1][1]
        bb_upper = bb[-1][2]
        bb_lower = bb[-1][0]
        bb_width = (bb_upper - bb_lower) if bb_upper and bb_lower else 0
        vol_avg = sum(volumes[-10:]) / 10 if len(volumes) >= 10 else volumes[-1]
        vol_spike = volumes[-1] / vol_avg if vol_avg else 1
        regime = 'A' if adx_val > 25 else ('B' if adx_val < 20 else 'B')
        # Log which endpoint was used for this symbol
        print(f'Price fetch for {sym}: {price} via {endpoint}', file=sys.stderr)
        # Strategy A conditions (trend)
        if regime == 'A':
            # BUY signal
            if macd_cur > signal_line[-1] and macd_prev <= signal_line[-2]:
                if 45 <= rsi_cur <= 65 and price > ema20_cur and price > ema50_cur:
                    # volume 20% above avg
                    if volumes[-1] > 1.2 * vol_avg:
                        signals.append({
                            'symbol': sym,
                            'direction': 'LONG',
                            'strategy': 'A',
                            'regime': regime,
                            'price': price
                        })
            # SHORT signal
            if macd_cur < signal_line[-1] and macd_prev >= signal_line[-2]:
                if 35 <= rsi_cur <= 55 and price < ema20_cur and price < ema50_cur:
                    if volumes[-1] > 1.2 * vol_avg:
                        signals.append({
                            'symbol': sym,
                            'direction': 'SHORT',
                            'strategy': 'A',
                            'regime': regime,
                            'price': price
                        })
        # Strategy B conditions (range)
        if regime == 'B':
            # BUY at lower BB
            if price <= bb_lower and rsi_cur < 35:
                # Stoch RSI not computed; skip
                signals.append({
                    'symbol': sym,
                    'direction': 'LONG',
                    'strategy': 'B',
                    'regime': regime,
                    'price': price
                })
            # SELL at upper BB
            if price >= bb_upper and rsi_cur > 65:
                signals.append({
                    'symbol': sym,
                    'direction': 'SHORT',
                    'strategy': 'B',
                    'regime': regime,
                    'price': price
                })
    # Output signals JSON
    print(json.dumps({'signals': signals}))

if __name__ == '__main__':
    main()
