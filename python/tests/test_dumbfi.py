from dumbfi import Dumbbt, hello

def test_hello():
    assert hello() == "Hello from rust!"

    # Run the account with the strategy function
    dbt = Dumbbt()

    # TODO
    # dbt.from_cash(1000)

    # TODO
    # dbt.load_prices("prices.csv", source="file")

    # Define a strategy
    def strategy(date):
        print(f"Running strategy for date: {date}")

    res = dbt.run("2021-01-01", "2021-12-31", strategy)
    print(res)
