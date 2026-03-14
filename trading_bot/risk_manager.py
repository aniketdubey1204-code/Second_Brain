"""Risk management module.
Provides utilities to enforce per‑trade risk limits, stop‑loss / take‑profit distances,
maximum open positions, daily loss caps, and volatility‑based suspensions.
"""
import math
from typing import Dict

class RiskManager:
    def __init__(self, config: Dict):
        self.risk_per_trade = config.get('risk_per_trade', 0.01)  # 1% of account balance
        self.max_open_positions = config.get('max_open_positions', 3)
        self.daily_loss_limit = config.get('daily_loss_limit', 0.05)  # 5% of balance
        self.volatility_threshold = config.get('volatility_threshold', 0.05)  # multiplier for ATR
        self.account_balance = config.get('initial_balance', 10000.0)
        self.daily_loss = 0.0
        self.open_positions = 0
        self.trading_halted = False
        self.last_drawdown = 0.0

    def reset_daily(self):
        self.daily_loss = 0.0
        self.trading_halted = False
        self.last_drawdown = 0.0
        self.open_positions = 0

    def update_balance(self, new_balance: float):
        self.account_balance = new_balance

    def can_open_position(self) -> bool:
        if self.trading_halted:
            return False
        if self.open_positions >= self.max_open_positions:
            return False
        if self.daily_loss >= self.account_balance * self.daily_loss_limit:
            return False
        return True

    def position_size(self, stop_loss_distance: float) -> float:
        """Calculate position size (in base currency units) given a stop‑loss distance.
        stop_loss_distance is expressed as a price difference (e.g., $10).
        """
        if stop_loss_distance <= 0:
            raise ValueError('stop_loss_distance must be positive')
        risk_amount = self.account_balance * self.risk_per_trade
        size = risk_amount / stop_loss_distance
        return size

    def evaluate_trade(self, entry_price: float, stop_loss: float, take_profit: float, atr: float) -> bool:
        """Return True if trade passes risk checks.
        - Volatility filter: ATR must be <= volatility_threshold * entry_price
        - Stop‑loss distance must be > 0
        """
        if atr > self.volatility_threshold * entry_price:
            # High volatility, suspend trading
            return False
        if stop_loss >= entry_price:
            # For long positions stop‑loss must be below entry (or above for short – simplified)
            return False
        if take_profit <= entry_price:
            return False
        return True

    def record_trade_outcome(self, pnl: float):
        """Update daily loss and open‑position count after a trade closes."""
        if pnl < 0:
            self.daily_loss += abs(pnl)
        self.open_positions = max(0, self.open_positions - 1)

    def halt_trading(self):
        self.trading_halted = True
