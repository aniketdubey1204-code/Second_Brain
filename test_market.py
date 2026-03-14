import yaml
import sys
from trading_bot.market_data import get_price, get_ohlcv

with open('trading_bot/config.yaml') as f:
    cfg = yaml.safe_load(f)

symbols = cfg.get('symbols', [])
for sym in symbols:
    try:
        price = get_price(sym)
        df = get_ohlcv(sym, timeframe='1m', limit=150)
        print(f"{sym}: price={price}, candles={len(df)}")
    except Exception as e:
        print(f"{sym}: ERROR {e}")
