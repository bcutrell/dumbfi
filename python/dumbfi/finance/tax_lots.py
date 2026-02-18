"""Tax lot tracking and tax-aware rebalancing."""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable


@dataclass
class TaxLot:
    """Single tax lot within a holding."""

    shares: float
    cost_basis: float  # per share
    purchase_date: datetime

    def value(self, price: float) -> float:
        """Market value of this lot."""
        return self.shares * price

    def total_cost(self) -> float:
        """Total cost basis."""
        return self.shares * self.cost_basis


@dataclass
class Holding:
    """A ticker position with target weight and tax lots."""

    ticker: str
    target_weight: float
    lots: list[TaxLot] = field(default_factory=list)


@dataclass
class TaxRates:
    """Capital gains tax rates."""

    short_term: float = 0.35
    long_term: float = 0.15


@dataclass
class Trade:
    """A buy or sell action."""

    ticker: str
    shares: float  # positive = buy, negative = sell
    amount: float  # dollar value (positive = buy, negative = sell)
    tax_cost: float = 0.0  # estimated tax impact (sells only)


@dataclass
class RebalanceConfig:
    """Controls rebalancing behavior."""

    tax_rates: TaxRates = field(default_factory=TaxRates)
    lot_selector: Callable[[list[TaxLot]], list[TaxLot]] = field(default=None)
    as_of: datetime = field(default_factory=datetime.now)
    min_trade_size: float = 0.0

    def __post_init__(self) -> None:
        if self.lot_selector is None:
            self.lot_selector = fifo


# --- Portfolio-level functions ---


def holding_value(h: Holding, price: float) -> float:
    """Sum of lot values for a holding."""
    return sum(lot.value(price) for lot in h.lots)


def portfolio_value(holdings: list[Holding], prices: dict[str, float]) -> float:
    """Total portfolio value."""
    return sum(holding_value(h, prices[h.ticker]) for h in holdings if h.ticker in prices)


def current_weights(holdings: list[Holding], prices: dict[str, float]) -> dict[str, float]:
    """Weight per ticker."""
    total = portfolio_value(holdings, prices)
    if total == 0:
        return {}
    return {h.ticker: holding_value(h, prices[h.ticker]) / total for h in holdings if h.ticker in prices}


def drift(holdings: list[Holding], prices: dict[str, float]) -> dict[str, float]:
    """Current weight minus target weight per ticker."""
    cw = current_weights(holdings, prices)
    return {h.ticker: cw.get(h.ticker, 0.0) - h.target_weight for h in holdings}


def drift_cost(holdings: list[Holding], prices: dict[str, float]) -> float:
    """Sum of squared drifts."""
    return sum(d * d for d in drift(holdings, prices).values())


# --- Lot-level functions ---


def unrealized_gain(lot: TaxLot, price: float) -> float:
    """Gain (positive) or loss (negative) for a lot."""
    return lot.value(price) - lot.total_cost()


def is_long_term(lot: TaxLot, as_of: datetime) -> bool:
    """True if held for more than 1 year."""
    return (as_of - lot.purchase_date) > timedelta(days=365)


def tax_cost(lot: TaxLot, price: float, as_of: datetime, rates: TaxRates) -> float:
    """Estimated tax impact of selling a lot."""
    gain = unrealized_gain(lot, price)
    rate = rates.long_term if is_long_term(lot, as_of) else rates.short_term
    return gain * rate


# --- Lot selectors ---

LotSelector = Callable[[list[TaxLot]], list[TaxLot]]


def fifo(lots: list[TaxLot]) -> list[TaxLot]:
    """Lots ordered by purchase date, oldest first."""
    return sorted(lots, key=lambda l: l.purchase_date)


def lifo(lots: list[TaxLot]) -> list[TaxLot]:
    """Lots ordered by purchase date, newest first."""
    return sorted(lots, key=lambda l: l.purchase_date, reverse=True)


def highest_cost_first(lots: list[TaxLot]) -> list[TaxLot]:
    """Lots ordered by cost basis, highest first."""
    return sorted(lots, key=lambda l: l.cost_basis, reverse=True)


# --- Rebalancing ---


def _calculate_sell_tax_cost(
    h: Holding, price: float, shares_to_sell: float, config: RebalanceConfig
) -> float:
    """Estimate tax cost of selling shares using the configured lot selector."""
    sorted_lots = config.lot_selector(h.lots)
    total_tax = 0.0
    remaining = shares_to_sell

    for lot in sorted_lots:
        if remaining <= 0:
            break
        sell_from_lot = min(lot.shares, remaining)
        partial_lot = TaxLot(
            shares=sell_from_lot,
            cost_basis=lot.cost_basis,
            purchase_date=lot.purchase_date,
        )
        total_tax += tax_cost(partial_lot, price, config.as_of, config.tax_rates)
        remaining -= sell_from_lot

    return total_tax


def rebalance(
    holdings: list[Holding], prices: dict[str, float], config: RebalanceConfig
) -> list[Trade]:
    """Generate trades to move holdings toward target weights."""
    total = portfolio_value(holdings, prices)
    if total == 0:
        return []

    trades: list[Trade] = []
    for h in holdings:
        price = prices.get(h.ticker)
        if price is None:
            continue
        current_val = holding_value(h, price)
        target_val = total * h.target_weight
        diff = target_val - current_val

        if abs(diff) < config.min_trade_size:
            continue

        if diff > 0:
            trades.append(Trade(ticker=h.ticker, shares=diff / price, amount=diff))
        else:
            sell_amount = -diff
            sell_shares = sell_amount / price
            tc = _calculate_sell_tax_cost(h, price, sell_shares, config)
            trades.append(Trade(ticker=h.ticker, shares=-sell_shares, amount=-sell_amount, tax_cost=tc))

    return trades


def total_tax_cost(trades: list[Trade]) -> float:
    """Sum tax cost across all trades."""
    return sum(t.tax_cost for t in trades)
