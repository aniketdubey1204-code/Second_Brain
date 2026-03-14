"""Portfolio manager module.
Tracks account balance, open positions, realized/unrealized P&L and key metrics.
"""
from typing import Dict, List

class Position:
    def __init__(self, symbol: str, side: str, entry_price: float, size: float, stop_loss: float, take_profit: float):
        self.symbol = symbol
        self.side = side  # 'buy' or 'sell'
        self.entry_price = entry_price
        self.size = size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.current_price = entry_price
        self.closed = False
        self.exit_price = None
        self.pnl = 0.0

    def update_price(self, price: float):
        self.current_price = price
        if not self.closed:
            if self.side == 'buy':
                self.pnl = (price - self.entry_price) * self.size
            else:
                self.pnl = (self.entry_price - price) * self.size

    def close(self, price: float):
        self.exit_price = price
        self.update_price(price)
        self.closed = True
        return self.pnl

class PortfolioManager:
    def __init__(self, initial_balance: float = 10000.0):
        self.account_balance = initial_balance
        self.open_positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_balance = initial_balance
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0

    def add_position(self, position: Position):
        self.open_positions.append(position)
        self.trade_count += 1

    def update_prices(self, price_dict: Dict[str, float]):
        self.unrealized_pnl = 0.0
        for pos in self.open_positions:
            if pos.symbol in price_dict:
                pos.update_price(price_dict[pos.symbol])
                self.unrealized_pnl += pos.pnl
        # Update drawdown
        total_equity = self.account_balance + self.unrealized_pnl
        if total_equity > self.peak_balance:
            self.peak_balance = total_equity
        drawdown = (self.peak_balance - total_equity) / self.peak_balance
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

    def close_position(self, position: Position, exit_price: float):
        pnl = position.close(exit_price)
        self.account_balance += pnl
        self.realized_pnl += pnl
        if pnl >= 0:
            self.win_count += 1
        else:
            self.loss_count += 1
        # Move from open to closed
        self.open_positions.remove(position)
        self.closed_positions.append(position)

    def summary(self) -> Dict:
        win_rate = (self.win_count / self.trade_count * 100) if self.trade_count else 0.0
        return {
            'account_balance': self.account_balance,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'max_drawdown': self.max_drawdown,
            'trade_count': self.trade_count,
            'win_rate': win_rate,
            'open_positions': len(self.open_positions),
        }
