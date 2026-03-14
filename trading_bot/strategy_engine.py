"""Strategy engine module.
Implements three example strategies and a factory to build a callable
strategy function based on supplied parameters.
"""
from typing import Callable, Dict

# Utility helpers
def is_cross_up(prev_short, prev_long, curr_short, curr_long):
    return prev_short <= prev_long and curr_short > curr_long

def is_cross_down(prev_short, prev_long, curr_short, curr_long):
    return prev_short >= prev_long and curr_short < curr_long

class TrendFollowingStrategy:
    def __init__(self, params: Dict):
        self.ema_short = params.get('ema_short', 20)
        self.ema_long = params.get('ema_long', 50)
        self.rsi_low = params.get('rsi_low', 45)
        self.rsi_high = params.get('rsi_high', 70)
        self.prev_ema_short = None
        self.prev_ema_long = None

    def __call__(self, snapshot: Dict):
        # snapshot contains: price, ema20, ema50, rsi, ...
        ema_s = snapshot.get(f'ema{self.ema_short}') or snapshot.get('ema20')
        ema_l = snapshot.get(f'ema{self.ema_long}') or snapshot.get('ema50')
        rsi = snapshot.get('rsi')
        signal = None
        if self.prev_ema_short is not None and self.prev_ema_long is not None:
            if is_cross_up(self.prev_ema_short, self.prev_ema_long, ema_s, ema_l) and self.rsi_low <= rsi <= self.rsi_high:
                signal = 'buy'
            elif is_cross_down(self.prev_ema_short, self.prev_ema_long, ema_s, ema_l) or rsi > 75:
                signal = 'sell'
        # Update previous values
        self.prev_ema_short = ema_s
        self.prev_ema_long = ema_l
        return signal

class GridStrategy:
    def __init__(self, params: Dict):
        self.grid_step = params.get('grid_step', 0.01)  # 1% grid step
        self.lower_bounds = {}
        self.upper_bounds = {}

    def __call__(self, snapshot: Dict, regime: str):
        if regime != 'sideways':
            return None
        price = snapshot['price']
        # Simple grid: if price is within lower 30% of a band, buy; if within upper 30%, sell
        # Here we define a synthetic band around the current price using grid_step
        lower = price * (1 - self.grid_step)
        upper = price * (1 + self.grid_step)
        if price <= lower * 1.1:
            return 'buy'
        if price >= upper * 0.9:
            return 'sell'
        return None

def build_strategy(params: Dict) -> Callable:
    """Factory that returns a function taking a snapshot dict (and optionally regime) and
    returning a trade signal: 'buy', 'sell', or None.
    """
    strategy_type = params.get('type', 'trend')
    if strategy_type == 'trend':
        trend = TrendFollowingStrategy(params)
        def _fn(snapshot: Dict, regime: str = None):
            return trend(snapshot)
        return _fn
    elif strategy_type == 'grid':
        grid = GridStrategy(params)
        def _fn(snapshot: Dict, regime: str = None):
            return grid(snapshot, regime)
        return _fn
    else:
        raise ValueError(f'Unsupported strategy type: {strategy_type}')
