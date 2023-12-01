"""
"""
import typing
import pandas as pd

class Account:

    def __init__(self, holdings: dict, cash: float = 0, tax_lots: dict = {}):
        self.cash = holdings.pop('$', cash)
        self.holdings = holdings
        self.tax_lots = tax_lots

    @classmethod
    def from_holdings(cls: typing.Type['Account'], holdings: dict) -> 'Account':
        return cls(holdings)

    @classmethod
    def from_tax_lots(cls: typing.Type['Account'], tax_lots: dict) -> 'Account':
        # sum up the holdings from the tax lots
        holdings = {}
        for symbol, lots in tax_lots.items():
            holdings[symbol] = sum(lot['shares'] for lot in lots)

        return cls(holdings, tax_lots=tax_lots)