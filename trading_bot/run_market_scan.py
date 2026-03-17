"""Market scan script for BTC, ETH, SOL.
Fetches recent OHLCV data via Binance, computes EMA, ATR, detects regime,
and logs a simple trade suggestion based on a grid strategy.
Outputs JSON to stdout.
"""
import json, sys
from market_data import get_ohlcv
from indicators import calculate_indicators
from regime_detector import detect_regime
import yaml

# Load config for volatility threshold
config_path = 'config.yaml'
with open(config_path, 'r') as f:
    cfg = yaml.safe_load(f)
vol_thresh = cfg.get('volatility_threshold', 0.05)

symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
results = []
for sym in symbols:
    try:
        df = get_ohlcv(sym, timeframe='5m', limit=200)
        ind = calculate_indicators(df)
        price = ind['price']
        ema_long = ind.get('ema50')
        atr = ind.get('atr')
        regime = detect_regime(price, ema_long, atr, vol_thresh)
        # Simple grid: 1% band
        lower = price * 0.99
        upper = price * 1.01
        if regime == 'sideways':
            if price < lower:
                signal = 'buy'
            elif price > upper:
                signal = 'sell'
            else:
                signal = None
        else:
            signal = None
        results.append({
            'symbol': sym,
            'price': price,
            'ema50': ema_long,
            'atr': atr,
            'regime': regime,
            'signal': signal,
        })
    except Exception as e:
        results.append({'symbol': sym, 'error': str(e)})

print(json.dumps({'timestamp': sys.argv[1] if len(sys.argv)>1 else None, 'results': results}, indent=2))
