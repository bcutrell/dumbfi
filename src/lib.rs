use chrono::NaiveDate;
use csv::ReaderBuilder;
use pyo3::prelude::*;
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
    pub lots: Vec<Lot>,
    pub cash: f64,
}

impl Portfolio {
    pub fn new(init_cash: f64) -> Self {
        Portfolio {
            lots: Vec::new(),
            cash: init_cash,
        }
    }

    pub fn add_lot(&mut self, lot: Lot) {
        // Check if there is enough cash to buy the lot
        if lot.shares * lot.purchase_price > self.cash {
            return;
        }
        self.cash -= lot.shares * lot.purchase_price;
        self.lots.push(lot);
    }

    pub fn total_value(&self, market_data: &MarketData, date: NaiveDate) -> f64 {
        let mut total = self.cash;
        for lot in &self.lots {
            if let Some(price) = market_data.get_price(date, &lot.ticker) {
                total += lot.shares * price.price;
            } else {
                eprintln!("Price not found for {} on {}", lot.ticker, date);
            }
        }
        total
    }

    pub fn print_holdings(&self) {
        println!("$:            {:>20.2}", self.cash);

        // sum lots for each ticker
        let mut ticker_shares: BTreeMap<String, f64> = BTreeMap::new();
        let mut ticker_lot_count: BTreeMap<String, usize> = BTreeMap::new();

        for lot in &self.lots {
            let shares = ticker_shares.entry(lot.ticker.clone()).or_insert(0.0);
            *shares += lot.shares;
            ticker_lot_count
                .entry(lot.ticker.clone())
                .and_modify(|e| *e += 1)
                .or_insert(1);
        }
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
Run backtest
-------------------------------------------------------------------------
*/

pub fn run_backtest(ctx: &Context) {
    let start_date = &ctx.config.start_date;
    let end_date = &ctx.config.end_date;
    let market_data = &ctx.market_data;
    let mut portfolio = ctx.portfolio.clone();

    // TODO
    // add rebalancer class that takes in a portfolio and market data
    // and determines the trades to make to rebalance the portfolio
    // rebalancer could be a rust impl, or a python class that calls
    // into rust to get the portfolio and market data
    // or an system call that takes in the portfolio and market data
    // and returns the trades to make

    // portfolio::run_backtest(&mut portfolio, market_data, start_date, end_date);
    // portfolio.add_target("AAPL", 1.0);
    // portfolio.print_profile();
    // portfolio.set_tax_rates(long_term=0.15, short_term=0.30);
    // portfolio.update_profile(long_term_tax_rate=0.15, short_term_tax_rate=0.30);
    // dumbbt::run_backtest(&mut portfolio, market_data, start_date, end_date);

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

    let ending_value = portfolio.total_value(&market_data, last_market_date);
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
        let portfolio = Portfolio::new(1000.0);
        assert_eq!(portfolio.cash, 1000.0);
        assert!(portfolio.lots.is_empty());
    }

    #[test]
    fn test_add_lot() {
        let mut portfolio = Portfolio::new(1000.0);
        let lot = Lot {
            ticker: "ASSET".to_string(),
            shares: 10.0,
            purchase_price: 100.0,
        };
        portfolio.add_lot(lot.clone());
        assert_eq!(portfolio.lots.len(), 1);
        assert_eq!(portfolio.lots[0], lot);
    }

    #[test]
    fn test_calculate_total_balance() {
        let mut portfolio = Portfolio::new(1000.0);
        let lot = Lot {
            ticker: "ASSET".to_string(),
            shares: 10.0,
            purchase_price: 100.0,
        };
        portfolio.add_lot(lot);

        let mut current_prices = HashMap::new();
        current_prices.insert("ASSET".to_string(), 110.0);

        let total_balance = portfolio.calculate_total_balance(&current_prices);
        assert_eq!(total_balance, 1100.0); // 0 cash + 1100 current value
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
