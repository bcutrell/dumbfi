"""
"""
import typing

CASH = '$'

class Account:

    def __init__(self, holdings: dict, cash: float = 0, tax_lots: dict = {}):
        self.cash = holdings.pop(CASH, cash)
        self.holdings = holdings
        self.tax_lots = tax_lots

    @classmethod
    def from_holdings(cls: typing.Type['Account'], holdings: dict) -> 'Account':
        return cls(holdings)

    @classmethod
    def from_tax_lots(cls: typing.Type['Account'], tax_lots: dict) -> 'Account':
        # assert that tax_lots have purchase_date, cost_basis, shares
        for symbol, lots in tax_lots.items():
            for lot in lots:
                assert 'purchase_date' in lot
                assert 'cost_basis' in lot
                assert 'shares' in lot

        # sum up the holdings from the tax lots
        holdings = {}
        for symbol, lots in tax_lots.items():
            holdings[symbol] = sum(lot['shares'] for lot in lots)

        return cls(holdings, tax_lots=tax_lots)

    def run(self, start_date: str, end_date: str, strategy: typing.Optional[typing.Callable] = None, **kwargs):
        """
        Run the account from start_date to end_date, executing strategy on each day.
        """
        pass
