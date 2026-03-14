from trading_bot.indicators import calculate_indicators
from trading_bot.market_data import get_ohlcv

df = get_ohlcv('BTCUSDT', timeframe='1m', limit=60)
ind = calculate_indicators(df)
print(ind)
