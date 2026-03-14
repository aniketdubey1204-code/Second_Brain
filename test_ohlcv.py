from trading_bot.market_data import get_ohlcv
import pandas as pd

df = get_ohlcv('BTCUSDT', timeframe='1m', limit=5)
print(df.head())
