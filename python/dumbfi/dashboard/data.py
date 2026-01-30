"""Fake portfolio generation and daily snapshot computation."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from dumbfi.finance.tax_lots import (
    Holding,
    TaxLot,
    TaxRates,
    RebalanceConfig,
    current_weights,
    drift,
    holding_value,
    is_long_term,
    portfolio_value,
    rebalance,
    unrealized_gain,
    fifo,
)


@dataclass
class LotSnapshot:
    """Snapshot of a single tax lot on a given day."""

    ticker: str
    lot_index: int
    value: float
    weight: float
    gain_pct: float
    is_long_term: bool


@dataclass
class DailySnapshot:
    """Portfolio state for one day."""

    date: str
    lots: list[LotSnapshot]
    weights: dict[str, float]
    drift: dict[str, float]
    total_value: float


# --- Portfolio setup ---

TARGET_WEIGHTS: dict[str, float] = {
    "AAPL": 0.35,
    "XOM": 0.25,
    "YUM": 0.20,
    "IBM": 0.20,
}


def _build_holdings(prices_df: pd.DataFrame) -> list[Holding]:
    """Create synthetic holdings with 2-3 lots per ticker using early CSV prices."""
    holdings: list[Holding] = []
    dates = prices_df.index.tolist()

    lot_specs: dict[str, list[tuple[int, float]]] = {
        # (date_index, share_count)
        "AAPL": [(0, 80), (10, 60), (30, 50)],
        "XOM": [(0, 120), (20, 100)],
        "YUM": [(5, 70), (15, 60), (25, 40)],
        "IBM": [(0, 55), (10, 70)],
    }

    for ticker, target in TARGET_WEIGHTS.items():
        lots: list[TaxLot] = []
        for date_idx, shares in lot_specs[ticker]:
            purchase_date = dates[date_idx].to_pydatetime()
            cost_basis = float(prices_df.iloc[date_idx][ticker])
            lots.append(TaxLot(shares=shares, cost_basis=cost_basis, purchase_date=purchase_date))
        holdings.append(Holding(ticker=ticker, target_weight=target, lots=lots))

    return holdings


def _load_prices(csv_path: str | None = None) -> pd.DataFrame:
    """Load sample_prices.csv, auto-detecting path."""
    if csv_path is None:
        candidates = [
            Path(__file__).resolve().parents[3] / "data" / "sample_prices.csv",
            Path("data/sample_prices.csv"),
        ]
        for p in candidates:
            if p.exists():
                csv_path = str(p)
                break
        if csv_path is None:
            raise FileNotFoundError("Cannot find data/sample_prices.csv")
    return pd.read_csv(csv_path, index_col=0, parse_dates=True)


def build_snapshots(csv_path: str | None = None) -> tuple[list[DailySnapshot], list[Holding]]:
    """Build daily snapshots from CSV price data and synthetic holdings."""
    prices_df = _load_prices(csv_path)
    holdings = _build_holdings(prices_df)
    snapshots: list[DailySnapshot] = []

    for date_idx in range(len(prices_df)):
        row = prices_df.iloc[date_idx]
        date_str = prices_df.index[date_idx].strftime("%Y-%m-%d")
        as_of = prices_df.index[date_idx].to_pydatetime()
        prices = {ticker: float(row[ticker]) for ticker in TARGET_WEIGHTS}

        total = portfolio_value(holdings, prices)
        if total == 0:
            continue

        cw = current_weights(holdings, prices)
        d = drift(holdings, prices)
        lot_snaps: list[LotSnapshot] = []

        for h in holdings:
            price = prices[h.ticker]
            for li, lot in enumerate(h.lots):
                lv = lot.value(price)
                gain = unrealized_gain(lot, price)
                gain_pct = (gain / lot.total_cost() * 100) if lot.total_cost() != 0 else 0.0
                lot_snaps.append(
                    LotSnapshot(
                        ticker=h.ticker,
                        lot_index=li,
                        value=lv,
                        weight=lv / total,
                        gain_pct=gain_pct,
                        is_long_term=is_long_term(lot, as_of),
                    )
                )

        snapshots.append(
            DailySnapshot(
                date=date_str,
                lots=lot_snaps,
                weights=cw,
                drift=d,
                total_value=total,
            )
        )

    return snapshots, holdings
