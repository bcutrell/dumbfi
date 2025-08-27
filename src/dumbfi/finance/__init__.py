"""
DumbFi Finance Library

Core finance utilities for portfolio management, risk modeling, and optimization.
Used by both educational notebooks and silly projects like the trading game.
"""

from .data import MarketData
from .portfolio import Portfolio, Position
from .risk import RiskModel, FactorModel
from .optimization import PortfolioOptimizer

__all__ = [
    "MarketData",
    "Portfolio",
    "Position",
    "RiskModel",
    "FactorModel",
    "PortfolioOptimizer",
]
