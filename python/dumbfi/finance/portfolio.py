"""Portfolio management and tracking."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Single position in a portfolio."""

    ticker: str
    quantity: float
    avg_cost: float
    current_price: Optional[float] = None

    @property
    def market_value(self) -> Optional[float]:
        """Current market value of the position."""
        return self.quantity * self.current_price if self.current_price else None

    @property
    def cost_basis(self) -> float:
        """Total cost basis of the position."""
        return self.quantity * self.avg_cost

    @property
    def unrealized_pnl(self) -> Optional[float]:
        """Unrealized profit/loss."""
        return self.market_value - self.cost_basis if self.current_price else None

    @property
    def unrealized_return(self) -> Optional[float]:
        """Unrealized return as percentage."""
        if self.current_price is None or self.cost_basis == 0:
            return None
        return (self.unrealized_pnl / self.cost_basis) * 100


class Portfolio:
    """Portfolio management for tracking positions and performance."""

    def __init__(self, initial_cash: float = 1_000_000, name: str = "Portfolio"):
        self.name = name
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.transaction_history: List[Dict] = []
        self._performance_history: List[Dict] = []

    def add_position(
        self, ticker: str, quantity: float, price: float, transaction_cost: float = 0.0
    ) -> bool:
        """Add or update a position. Returns True if successful."""
        total_cost = abs(quantity) * price + transaction_cost

        if quantity > 0 and total_cost > self.cash:
            logger.warning(f"Insufficient cash: need ${total_cost:.2f}, have ${self.cash:.2f}")
            return False

        self._record_transaction(ticker, quantity, price, transaction_cost)

        if ticker in self.positions:
            return self._update_existing_position(ticker, quantity, price, transaction_cost)
        return self._create_new_position(ticker, quantity, price, total_cost)

    def _record_transaction(
        self, ticker: str, quantity: float, price: float, transaction_cost: float
    ) -> None:
        """Record a transaction in history."""
        self.transaction_history.append({
            "timestamp": datetime.now(),
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "transaction_cost": transaction_cost,
            "type": "BUY" if quantity > 0 else "SELL",
        })

    def _update_existing_position(
        self, ticker: str, quantity: float, price: float, transaction_cost: float
    ) -> bool:
        """Update an existing position with buy or sell."""
        existing = self.positions[ticker]
        total_cost = abs(quantity) * price + transaction_cost

        if quantity > 0:
            new_quantity = existing.quantity + quantity
            total_cost_basis = existing.cost_basis + (quantity * price)
            existing.quantity = new_quantity
            existing.avg_cost = total_cost_basis / new_quantity if new_quantity > 0 else 0
            self.cash -= total_cost
        else:
            sell_quantity = abs(quantity)
            if sell_quantity > existing.quantity:
                logger.warning(f"Cannot sell {sell_quantity} shares, only have {existing.quantity}")
                return False
            existing.quantity -= sell_quantity
            self.cash += sell_quantity * price - transaction_cost
            if existing.quantity <= 0:
                del self.positions[ticker]
        return True

    def _create_new_position(
        self, ticker: str, quantity: float, price: float, total_cost: float
    ) -> bool:
        """Create a new position."""
        if quantity <= 0:
            logger.warning(f"Cannot sell {ticker}, no existing position")
            return False
        self.positions[ticker] = Position(ticker, quantity, price)
        self.cash -= total_cost
        return True

    def update_prices(self, prices: Dict[str, float]) -> None:
        """Update current prices for all positions."""
        for ticker, position in self.positions.items():
            if ticker in prices:
                position.current_price = prices[ticker]

    def get_total_value(self) -> float:
        """Get total portfolio value (cash + positions)."""
        positions_value = sum(
            pos.market_value or pos.cost_basis for pos in self.positions.values()
        )
        return self.cash + positions_value

    def get_positions_value(self) -> float:
        """Get total value of positions (excluding cash)."""
        return sum(
            pos.market_value or pos.cost_basis for pos in self.positions.values()
        )

    def get_cash_weight(self) -> float:
        """Get cash as percentage of total portfolio."""
        total_value = self.get_total_value()
        return (self.cash / total_value * 100) if total_value > 0 else 0

    def get_position_weights(self) -> Dict[str, float]:
        """Get position weights as percentage of total portfolio."""
        total_value = self.get_total_value()
        if total_value <= 0:
            return {}

        weights = {}
        for ticker, position in self.positions.items():
            market_value = position.market_value or position.cost_basis
            weights[ticker] = (market_value / total_value) * 100

        return weights

    def get_unrealized_pnl(self) -> Dict[str, float]:
        """Get unrealized P&L for all positions."""
        return {
            ticker: pos.unrealized_pnl or 0 for ticker, pos in self.positions.items()
        }

    def get_total_unrealized_pnl(self) -> float:
        """Get total unrealized P&L across all positions."""
        return sum(self.get_unrealized_pnl().values())

    def get_realized_pnl(self) -> float:
        """Calculate realized P&L from transaction history using FIFO."""
        realized_pnl = 0.0
        position_cost_tracking = {}

        for transaction in self.transaction_history:
            ticker = transaction["ticker"]
            quantity = transaction["quantity"]
            price = transaction["price"]

            if quantity > 0:  # Buy
                if ticker not in position_cost_tracking:
                    position_cost_tracking[ticker] = []
                position_cost_tracking[ticker].append((quantity, price))
            else:  # Sell
                sell_quantity = abs(quantity)
                if ticker in position_cost_tracking:
                    # FIFO basis
                    remaining_to_sell = sell_quantity
                    while remaining_to_sell > 0 and position_cost_tracking[ticker]:
                        buy_quantity, buy_price = position_cost_tracking[ticker][0]

                        if buy_quantity <= remaining_to_sell:
                            # Sell entire lot
                            realized_pnl += buy_quantity * (price - buy_price)
                            remaining_to_sell -= buy_quantity
                            position_cost_tracking[ticker].pop(0)
                        else:
                            # Partial sell
                            realized_pnl += remaining_to_sell * (price - buy_price)
                            position_cost_tracking[ticker][0] = (
                                buy_quantity - remaining_to_sell,
                                buy_price,
                            )
                            remaining_to_sell = 0

        return realized_pnl

    def get_total_return(self) -> float:
        """Get total return since inception."""
        current_value = self.get_total_value()
        return ((current_value / self.initial_cash) - 1) * 100

    def record_snapshot(self, timestamp: Optional[datetime] = None) -> None:
        """Record a snapshot of portfolio performance."""
        if timestamp is None:
            timestamp = datetime.now()

        snapshot = {
            "timestamp": timestamp,
            "total_value": self.get_total_value(),
            "cash": self.cash,
            "positions_value": self.get_positions_value(),
            "unrealized_pnl": self.get_total_unrealized_pnl(),
            "realized_pnl": self.get_realized_pnl(),
            "total_return": self.get_total_return(),
            "num_positions": len(self.positions),
            "position_weights": self.get_position_weights().copy(),
        }

        self._performance_history.append(snapshot)

    def get_performance_history(self) -> pd.DataFrame:
        """Get performance history as DataFrame."""
        if not self._performance_history:
            return pd.DataFrame()

        df = pd.DataFrame(self._performance_history)
        df.set_index("timestamp", inplace=True)
        return df

    def calculate_performance_metrics(
        self, risk_free_rate: float = 0.02
    ) -> Dict[str, float]:
        """Calculate performance metrics including Sharpe ratio and max drawdown."""
        df = self.get_performance_history()
        if len(df) < 2:
            return {}

        # Calculate returns
        df["returns"] = df["total_value"].pct_change()
        returns = df["returns"].dropna()

        if len(returns) == 0:
            return {}

        # Annualize based on frequency
        trading_days_per_year = 252
        periods_per_year = trading_days_per_year / len(returns) * len(df)

        metrics = {
            "total_return": self.get_total_return(),
            "annualized_return": (returns.mean() * periods_per_year) * 100,
            "volatility": (returns.std() * np.sqrt(periods_per_year)) * 100,
            "sharpe_ratio": (
                (
                    (returns.mean() * periods_per_year - risk_free_rate)
                    / (returns.std() * np.sqrt(periods_per_year))
                )
                if returns.std() > 0
                else 0
            ),
            "max_drawdown": self._calculate_max_drawdown(df),
            "win_rate": (returns > 0).mean() * 100,
            "avg_win": returns[returns > 0].mean() * 100 if (returns > 0).any() else 0,
            "avg_loss": returns[returns < 0].mean() * 100 if (returns < 0).any() else 0,
        }

        return metrics

    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown from peak."""
        if "total_value" not in df.columns:
            return 0.0

        peak = df["total_value"].expanding().max()
        drawdown = ((df["total_value"] - peak) / peak) * 100
        return drawdown.min()

    def rebalance_to_target(
        self,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        transaction_cost_rate: float = 0.001,
    ) -> Dict[str, float]:
        """Rebalance portfolio to target weights. Returns executed trades."""
        self.update_prices(current_prices)
        total_value = self.get_total_value()
        current_weights = self.get_position_weights()
        trades = {}

        for ticker, target_weight in target_weights.items():
            if ticker not in current_prices:
                logger.warning(f"No price data for {ticker}, skipping")
                continue

            current_weight = current_weights.get(ticker, 0)
            weight_diff = target_weight - current_weight

            if abs(weight_diff) > 0.01:
                target_value = (target_weight / 100) * total_value
                current_value = (current_weight / 100) * total_value
                trade_value = target_value - current_value
                price = current_prices[ticker]
                quantity = trade_value / price

                if quantity != 0:
                    transaction_cost = abs(trade_value) * transaction_cost_rate
                    if self.add_position(ticker, quantity, price, transaction_cost):
                        trades[ticker] = quantity

        return trades

    def summary(self) -> Dict[str, Any]:
        """Get portfolio summary."""
        weights = self.get_position_weights()

        return {
            "name": self.name,
            "total_value": self.get_total_value(),
            "cash": self.cash,
            "cash_weight": self.get_cash_weight(),
            "positions_value": self.get_positions_value(),
            "num_positions": len(self.positions),
            "total_return": self.get_total_return(),
            "unrealized_pnl": self.get_total_unrealized_pnl(),
            "realized_pnl": self.get_realized_pnl(),
            "largest_position": max(weights.items(), key=lambda x: x[1])
            if weights
            else None,
            "position_weights": weights,
        }

    def __repr__(self) -> str:
        summary = self.summary()
        return (
            f"Portfolio(name='{summary['name']}', value=${summary['total_value']:,.2f}, "
            f"positions={summary['num_positions']}, return={summary['total_return']:.2f}%)"
        )
