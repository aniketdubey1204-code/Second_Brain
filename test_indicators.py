import yaml
import pandas as pd
from trading_bot.market_data import get_ohlcv
from trading_bot.indicators import calculate_indicators

with open('trading_bot/config.yaml') as f:
    cfg = yaml.safe_load(f)

symbols = cfg.get('symbols', [])
for sym in symbols:
    df = get_ohlcv(sym, timeframe='1m', limit=150)
    inds = calculate_indicators(df)
    missing = [k for k, v in inds.items() if pd.isna(v)]
    if missing:
        print(f"{sym}: MISSING {missing}")
    else:
        print(f"{sym}: all indicators present")
