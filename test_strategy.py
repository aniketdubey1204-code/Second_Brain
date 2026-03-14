import yaml
from trading_bot.market_data import get_ohlcv
from trading_bot.indicators import calculate_indicators
from trading_bot.regime_detector import detect_regime
from trading_bot.strategy_engine import build_strategy

with open('trading_bot/config.yaml') as f:
    cfg = yaml.safe_load(f)

sym = cfg['symbols'][0]
# fetch enough candles
df = get_ohlcv(sym, timeframe='1m', limit=150)
snapshot = calculate_indicators(df)
# regime detection
regime = detect_regime(
    price=snapshot['price'],
    ema100=snapshot['ema100'],
    ema20=snapshot['ema20'],
    ema50=snapshot['ema50'],
    atr=snapshot['atr'],
    vol_thresh=cfg.get('volatility_threshold',0.05)
)
# build a trend strategy
strategy = build_strategy({'type':'trend'})
signal = strategy(snapshot, regime)
print('Strategy signal:', signal)
