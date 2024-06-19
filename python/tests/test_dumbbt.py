from dumbfi import dumbbt


def test_from_holdings():
    acct = dumbbt.Account.from_holdings({"AAPL": 100, "$": 100})
    assert isinstance(acct, dumbbt.Account)
    assert acct.cash == 100
    assert acct.holdings == {"AAPL": 100}
    assert acct.tax_lots == {}


def test_from_tax_lots():
    tax_lots = {
        "AAPL": [
            {"shares": 100, "cost_basis": 100, "purchase_date": "2020-01-01"},
            {"shares": 100, "cost_basis": 200, "purchase_date": "2020-01-02"},
        ],
    }
    acct = dumbbt.Account.from_tax_lots(tax_lots)
    assert isinstance(acct, dumbbt.Account)

    assert acct.cash == 0
    assert acct.holdings == {"AAPL": 200}
    assert acct.tax_lots == tax_lots

    # tax lot must have purchase_date, cost_basis, shares
    tax_lots = {
        "AAPL": [
            {"shares": 100, "cost_basis": 100},
        ],
    }
    try:
        acct = dumbbt.Account.from_tax_lots(tax_lots)
        assert False
    except AssertionError:
        pass


def test_run():
    acct = dumbbt.Account.from_holdings({"AAPL": 100, "$": 100})
    assert acct.cash == 100
    assert acct.holdings == {"AAPL": 100}
    assert acct.tax_lots == {}

    def strategy(acct, current_date, **kwargs):
        pass

    acct.run("2020-01-01", "2020-01-02", strategy=strategy)
    assert acct.cash == 100
    assert acct.holdings == {"AAPL": 100}
    assert acct.tax_lots == {}
