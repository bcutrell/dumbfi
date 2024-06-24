use std::collections::HashMap;
use csv::ReaderBuilder;
use pyo3::prelude::*;
use chrono::{NaiveDate, Datelike};
use pyo3::types::{PyDate, PyDict, PyFunction, PyTuple};
use serde::Deserialize;
use std::collections::BTreeMap;
use std::error::Error;
use std::fs;
use toml;

/*
-------------------------------------------------------------------------
Python bindings
-------------------------------------------------------------------------
*/

#[pyfunction]
fn hello() -> PyResult<String> {
    Ok("Hello from rust!".into())
}

/// A Python module implemented in Rust.
#[pymodule]
fn _lowlevel(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello, m)?)?;
    m.add_class::<Dumbbt>()?;
    Ok(())
}

/*
-------------------------------------------------------------------------
Config
-------------------------------------------------------------------------
*/

#[derive(Debug, Deserialize)]
pub struct Config {
    pub start_date: String,
    pub end_date: String,
    pub init_cash: f64,
    pub prices_file: String,
}

impl Config {
    pub fn from_toml_file_path(file_path: &str) -> Result<Self, Box<dyn Error>> {
        // Read the TOML configuration file content into a string
        let config_content = fs::read_to_string(file_path)?;

        // Parse the TOML string into a Config instance
        let config: Self = toml::from_str(&config_content)?;

        Ok(config)
    }
}

/*
-------------------------------------------------------------------------
Context
-------------------------------------------------------------------------
*/

pub struct Context {
    pub config: Config,
    pub portfolio: Portfolio,
    pub market_data: MarketData,
}

/*
-------------------------------------------------------------------------
Market data
-------------------------------------------------------------------------
*/

#[derive(Debug)]
pub struct StockPrice {
    pub date: NaiveDate,
    pub ticker: String,
    pub price: f64,
}

type DateTickerKey = (NaiveDate, String);

pub struct MarketData {
    pub prices: BTreeMap<DateTickerKey, StockPrice>,
}

impl MarketData {
    pub fn new() -> Self {
        MarketData {
            prices: BTreeMap::new(),
        }
    }

    pub fn with_prices_file(mut self, file_path: &str) -> Result<Self, Box<dyn Error>> {
        let file = fs::File::open(file_path)?;
        let mut rdr = ReaderBuilder::new().has_headers(true).from_reader(file);
        let headers = rdr.headers()?.clone();

        for result in rdr.records() {
            let record = result?;
            let date = NaiveDate::parse_from_str(&record[0], "%Y-%m-%d")?;

            for (i, header) in headers.iter().enumerate().skip(1) {
                let ticker = header.to_string();
                let price: f64 = record[i].parse()?;
                self.add_price(date, ticker, price);
            }
        }
        Ok(self)
    }

    fn add_price(&mut self, date: NaiveDate, ticker: String, price: f64) {
        let key = (date, ticker.clone());
        self.prices.insert(
            key,
            StockPrice {
                date,
                ticker,
                price,
            },
        );
    }

    pub fn get_price(&self, date: NaiveDate, ticker: &str) -> Option<&StockPrice> {
        let key = (date, ticker.to_string());
        self.prices.get(&key)
    }

    /// Returns true if there are prices in the market data on the given date
    pub fn has_prices_on_date(&self, date: NaiveDate) -> bool {
        // Start the range at the beginning of the day with an empty string.
        let start = (date, "".to_string());
        // End the range at the end of the day with a string that
        // is guaranteed to be greater than any possible valid string.
        let end = (date, "\u{FFFF}".to_string());

        self.prices.range(start..=end).next().is_some()
    }

    pub fn get_prices_in_range(
        &self,
        ticker: &str,
        start_date: NaiveDate,
        end_date: NaiveDate,
    ) -> Vec<&StockPrice> {
        self.prices
            .range((start_date, ticker.to_string())..=(end_date, ticker.to_string()))
            .map(|(_, price)| price)
            .collect()
    }
}

/*
-------------------------------------------------------------------------
Portfolio
-------------------------------------------------------------------------
*/

#[derive(Debug, Clone, PartialEq)]
pub struct Lot {
    pub ticker: String,
    pub shares: f64,
    pub purchase_price: f64,
}

#[derive(Debug, Clone)]
pub struct Portfolio {
    pub cash: f64,
    pub lots: HashMap<String, Vec<Lot>>,
}

impl Portfolio {
    pub fn new(cash: f64, lots: HashMap<String, Vec<Lot>>) -> Self {
        Portfolio { cash, lots }
    }

    pub fn from_cash(init_cash: f64) -> Self {
        Portfolio {
            cash: init_cash,
            lots: HashMap::new(),
        }
    }

    pub fn from_positions(positions: Vec<Lot>) -> Self {
        let mut lots: HashMap<String, Vec<Lot>> = HashMap::new();
        for lot in positions {
            lots.entry(lot.ticker.clone()).or_insert(Vec::new()).push(lot);
        }
        Portfolio { cash: 0.0, lots }
    }

    pub fn from_lots(lots: HashMap<String, Vec<Lot>>) -> Self {
        Portfolio { cash: 0.0, lots }
    }

    pub fn add_cash(&mut self, amount: f64) {
        self.cash += amount;
    }

    pub fn buy_lot(&mut self, lot: Lot) {
        // Check if there is enough cash to buy the lot
        // no margin trading at the moment
        if lot.shares * lot.purchase_price > self.cash {
            return;
        }
        self.cash -= lot.shares * lot.purchase_price;
        self.lots.entry(lot.ticker.clone()).or_insert(Vec::new()).push(lot);
    }

    pub fn add_lot(&mut self, lot: Lot) {
        self.lots.entry(lot.ticker.clone()).or_insert(Vec::new()).push(lot);
    }

    pub fn calc_total_value(&self, market_data: &MarketData, date: NaiveDate) -> f64 {
        let mut total = self.cash;
        for (ticker, lots) in &self.lots {
            for lot in lots {
                if let Some(price) = market_data.get_price(date, ticker) {
                    total += lot.shares * price.price;
                } else {
                    eprintln!("Price not found for {} on {}", ticker, date);
                }
            }
        }
        total
    }

    pub fn print_holdings(&self) {
        // Sum lots for each ticker
        let mut ticker_shares: BTreeMap<String, f64> = BTreeMap::new();
        let mut ticker_lot_count: BTreeMap<String, usize> = BTreeMap::new();

        for (ticker, lots) in &self.lots {
            for lot in lots {
                let shares = ticker_shares.entry(ticker.clone()).or_insert(0.0);
                *shares += lot.shares;
                ticker_lot_count
                    .entry(ticker.clone())
                    .and_modify(|e| *e += 1)
                    .or_insert(1);
            }
        }

        println!("$:            {:>20.2}", self.cash);
        for (ticker, shares) in ticker_shares {
            println!(
                "{}:         {:>20.2} ({} lots)",
                ticker, shares, ticker_lot_count[&ticker]
            );
        }
    }
}

/*
-------------------------------------------------------------------------
Rebalancer
-------------------------------------------------------------------------
*/

/*
-------------------------------------------------------------------------
Dumbbt
-------------------------------------------------------------------------
*/

#[pyclass]
struct Dumbbt {
    portfolio: Portfolio,
    market_data: MarketData,
}

#[pymethods]
impl Dumbbt {
    #[new]
    fn new() -> Self {
        Dumbbt {
            portfolio: Portfolio::from_cash(0.0),
            market_data: MarketData::new(),
        }
    }

    fn run(&self, start_date: &str, end_date: &str, py: Python, strategy: Py<PyFunction>) -> PyResult<Py<PyDict>> {
        let start_date = NaiveDate::parse_from_str(start_date, "%Y-%m-%d").map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        let end_date = NaiveDate::parse_from_str(end_date, "%Y-%m-%d").map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

        let mut current_date = start_date;
        let mut results: HashMap<String, Vec<f64>> = HashMap::new();
        while current_date <= end_date {
            if !self.market_data.has_prices_on_date(current_date) {
                current_date = current_date.succ_opt().unwrap();
                continue;
            }

            let py_date = PyDate::new(py, current_date.year(), current_date.month() as u8, current_date.day() as u8)?;

            if let Err(e) = strategy.call1(py, PyTuple::new(py, &[py_date])) {
                return Err(e);
            }
            results.insert(current_date.to_string(), vec![1.0]);

            current_date = current_date.succ_opt().unwrap();
        }

        // Convert the Rust HashMap to a Python dictionary
        let py_results = PyDict::new(py);
        for (key, values) in results {
            let py_values = values.iter().map(|v| v.into_py(py)).collect::<Vec<_>>();
            py_results.set_item(key, py_values)?;
        }

        Ok(py_results.into())
    }
}

/*
-------------------------------------------------------------------------
Run backtest
-------------------------------------------------------------------------
*/

pub fn run_backtest(ctx: &Context) {
    let start_date = &ctx.config.start_date;
    let end_date = &ctx.config.end_date;
    let market_data = &ctx.market_data;
    let mut portfolio = ctx.portfolio.clone();

    // Before backtest
    println!("Start date:   {:>20}", start_date);
    println!("End date:     {:>20}", end_date);
    println!("Initial cash: {:>20.2}", portfolio.cash);

    // Parse the start and end dates
    let start_date = NaiveDate::parse_from_str(start_date, "%Y-%m-%d").unwrap();
    let end_date = NaiveDate::parse_from_str(end_date, "%Y-%m-%d").unwrap();

    let mut current_date = start_date;
    let mut last_market_date = start_date;

    while current_date <= end_date {
        if !market_data.has_prices_on_date(current_date) {
            current_date = current_date.succ_opt().unwrap();
            continue;
        }

        // TODO
        // add rebalancer class that takes in a portfolio and market data
        // and determines the trades to make to rebalance the portfolio
        // rebalancer could be a rust impl, or a python class that calls
        // into rust to get the portfolio and market data
        // or an system call that takes in the portfolio and market data
        // and returns the trades to make

        // buy one share of AAPL
        let price = market_data.get_price(current_date, "AAPL");
        if let Some(price) = price {
            let lot = Lot {
                ticker: price.ticker.clone(),
                shares: 1.0,
                purchase_price: price.price,
            };
            portfolio.add_lot(lot);
            last_market_date = current_date;
        }
        current_date = current_date.succ_opt().unwrap();
    }

    let ending_value = portfolio.calc_total_value(&market_data, last_market_date);

    println!("Ending cash:  {:>20.2}", portfolio.cash);
    println!("Ending value: {:>20.2}", ending_value);
    println!(
        "Total return: {:>20.2}",
        ending_value - ctx.config.init_cash
    );
    println!("Ending Portfolio holdings:");
    portfolio.print_holdings();
}

/*
-------------------------------------------------------------------------
Tests
-------------------------------------------------------------------------
*/

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_portfolio_init() {
        let portfolio = Portfolio::from_cash(1000.0);
        assert_eq!(portfolio.cash, 1000.0);
        assert!(portfolio.lots.is_empty());
    }

    #[test]
    fn test_add_lot() {
        let mut portfolio = Portfolio::from_cash(1000.0);
        let lot = Lot {
            ticker: "ASSET".to_string(),
            shares: 10.0,
            purchase_price: 100.0,
        };
        portfolio.add_lot(lot.clone());
        assert_eq!(portfolio.lots[&lot.ticker].len(), 1);
        assert_eq!(portfolio.lots[&lot.ticker][0], lot);
    }

    #[test]
    fn test_calc_total_value() {
        let mut portfolio = Portfolio::from_cash(1000.0);
        let lot = Lot {
            ticker: "MSFT".to_string(),
            shares: 1.0,
            purchase_price: 100.0,
        };
        portfolio.add_lot(lot.clone());

        let mut market_data = MarketData::new();
        let date = NaiveDate::from_ymd_opt(2021, 1, 1).expect("Invalid date");
        market_data.add_price(date, "MSFT".to_string(), 100.0);

        let total_value = portfolio.calc_total_value(&market_data, date);
        assert_eq!(total_value, 1100.0); // 1000 cash + 1 lot of MSFT at 100

        portfolio.add_lot(lot.clone());
        let total_value = portfolio.calc_total_value(&market_data, date);
        assert_eq!(total_value, 1200.0); // 1000 cash + 2 lots of MSFT at 100
    }

    #[test]
    fn test_config_parsing() {
        let toml_str = r#"
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        init_cash = 1000.0
        prices_file = "prices.csv"
    "#;

        let config: Config = toml::from_str(toml_str).unwrap();
        assert_eq!(config.start_date, "2023-01-01");
        assert_eq!(config.end_date, "2023-12-31");
        assert_eq!(config.init_cash, 1000.0);
        assert_eq!(config.prices_file, "prices.csv");
    }

    #[test]
    fn test_new_market_data() {
        let market_data = MarketData::new();
        assert!(market_data.prices.is_empty());
    }

    #[test]
    fn test_add_and_get_stock_price() {
        let mut market_data = MarketData::new();
        let date = NaiveDate::from_ymd_opt(2021, 1, 1).expect("Invalid date");
        market_data.add_price(date, "MSFT".to_string(), 217.69);

        let price = market_data.get_price(date, "MSFT");
        assert!(price.is_some());
        let price = price.unwrap();
        assert_eq!(price.date, date);
        assert_eq!(price.ticker, "MSFT");
        assert_eq!(price.price, 217.69);
    }

    #[test]
    fn test_get_prices_in_range() {
        let mut market_data = MarketData::new();
        let date0 = NaiveDate::from_ymd_opt(2021, 1, 1).expect("Invalid date");
        let date1 = NaiveDate::from_ymd_opt(2021, 1, 2).expect("Invalid date");
        let date2 = NaiveDate::from_ymd_opt(2021, 1, 3).expect("Invalid date");

        market_data.add_price(date0, "MSFT".to_string(), 217.00);
        market_data.add_price(date1, "MSFT".to_string(), 218.00);
        market_data.add_price(date2, "MSFT".to_string(), 219.00);

        let prices = market_data.get_prices_in_range("MSFT", date0, date2);
        assert_eq!(prices.len(), 3);
        assert_eq!(prices[0].date, date0);
        assert_eq!(prices[1].date, date1);
        assert_eq!(prices[2].date, date2);

        assert_eq!(prices[0].price, 217.00);
        assert_eq!(prices[1].price, 218.00);
        assert_eq!(prices[2].price, 219.00);

        assert_eq!(prices[0].ticker, "MSFT");
        assert_eq!(prices[1].ticker, "MSFT");
        assert_eq!(prices[2].ticker, "MSFT");
    }

    #[test]
    fn test_get_price_not_found() {
        let market_data = MarketData::new();
        let date = NaiveDate::from_ymd_opt(2021, 1, 1).expect("Invalid date");
        assert!(market_data.get_price(date, "MSFT").is_none());
    }
}
