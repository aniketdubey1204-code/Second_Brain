"""Indicator engine.
Computes technical indicators required by strategies using pandas‑ta (ta) library.
Exports a single function ``calculate_indicators(df)`` that returns a dict of values.
"""
import pandas as pd
import ta
from typing import Dict

def calculate_indicators(df: pd.DataFrame) -> Dict:
    """Given a DataFrame with columns ['close','high','low','open','volume']
    return a dictionary with the latest indicator snapshot:
    {
        'price': float,
        'ema20': float,
        'ema50': float,
        'rsi': float,
        'macd': float,
        'macd_signal': float,
        'bb_upper': float,
        'bb_lower': float,
        'atr': float,
    }
    """
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    # EMA
    ema20 = ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]
    # RSI
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]
    # MACD
    macd_obj = ta.trend.MACD(close)
    macd = macd_obj.macd().iloc[-1]
    macd_signal = macd_obj.macd_signal().iloc[-1]
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]
    # ATR
    atr = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range().iloc[-1]
    snapshot = {
        'price': float(close.iloc[-1]),
        'ema20': float(ema20),
        'ema50': float(ema50),
        'rsi': float(rsi),
        'macd': float(macd),
        'macd_signal': float(macd_signal),
        'bb_upper': float(bb_upper),
        'bb_lower': float(bb_lower),
        'atr': float(atr),
    }
    return snapshot
