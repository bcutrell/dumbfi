import pandas as pd
from dumbfi import dumbbt

def test_from_holdings():
    acct = dumbbt.Account.from_holdings({'AAPL': 100, '$': 100})
    assert isinstance(acct, dumbbt.Account)
    assert acct.cash == 100
    assert acct.holdings == { 'AAPL': 100 }
    assert acct.tax_lots == {}

def test_from_tax_lots():
    tax_lots = {
        'AAPL': [
            {'shares': 100, 'cost_basis': 100, 'trade_date': pd.Timestamp('2020-01-01')},
            {'shares': 100, 'cost_basis': 200, 'trade_date': pd.Timestamp('2020-01-02')},
        ],
    }
    acct = dumbbt.Account.from_tax_lots(tax_lots)
    assert isinstance(acct, dumbbt.Account)

    assert acct.cash == 0
    assert acct.holdings == { 'AAPL': 200 }
    assert acct.tax_lots == tax_lots