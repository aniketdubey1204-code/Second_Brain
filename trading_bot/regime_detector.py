"""Regime detector module.
Classifies market regime based on long‑term EMA and ATR volatility.
"""
from typing import Literal

def detect_regime(price: float, ema_long: float, atr: float, volatility_threshold: float) -> Literal['bull','bear','sideways']:
    """Simple regime logic:
    - bull: price > ema_long and atr <= volatility_threshold
    - bear: price < ema_long and atr <= volatility_threshold
    - sideways: otherwise (high volatility or near ema)
    """
    if atr > volatility_threshold:
        return 'sideways'
    if price > ema_long:
        return 'bull'
    if price < ema_long:
        return 'bear'
    return 'sideways'
