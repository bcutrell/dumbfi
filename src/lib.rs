use chrono::NaiveDate;
use csv::ReaderBuilder;
use pyo3::prelude::*;
use std::collections::BTreeMap;
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;

/// Prints a message.
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

#[derive(Debug, serde::Deserialize)]
pub struct Config {
    pub start_date: String,
    pub end_date: String,
    pub init_cash: f64,
    pub prices_file: String,
}

pub struct Context {
    pub config: Config,
    pub portfolio: Portfolio,
    pub market_data: MarketData,
}

#[derive(Debug)]
struct StockPrice {
    date: NaiveDate,
    ticker: String,
    price: f64,
}

type DateTickerKey = (NaiveDate, String);

pub struct MarketData {
    prices: BTreeMap<DateTickerKey, StockPrice>,
}

impl MarketData {
    pub fn new() -> Self {
        MarketData {
            prices: BTreeMap::new(),
        }
    }

    fn add_stock_price(&mut self, date: NaiveDate, ticker: String, price: f64) {
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

    fn get_price(&self, date: NaiveDate, ticker: &str) -> Option<&StockPrice> {
        let key = (date, ticker.to_string());
        self.prices.get(&key)
    }

    fn get_prices_in_range(
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

    fn load_prices_from_csv(file_path: &str) -> Result<Self, Box<dyn Error>> {
        let mut market_data = MarketData::new();
        let file = File::open(file_path)?;
        let mut rdr = ReaderBuilder::new().has_headers(true).from_reader(file);

        let headers = rdr.headers()?.clone();

        for result in rdr.records() {
            let record = result?;
            let date = NaiveDate::parse_from_str(&record[0], "%Y-%m-%d")?;

            for (i, header) in headers.iter().enumerate().skip(1) {
                let ticker = header.to_string();
                let price: f64 = record[i].parse()?;
                market_data.add_stock_price(date, ticker, price);
            }
        }

        Ok(market_data)
    }
}

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
        self.cash -= lot.shares * lot.purchase_price;
        self.lots.push(lot);
    }

    pub fn calculate_total_balance(&self, current_prices: &HashMap<String, f64>) -> f64 {
        let mut total_balance = self.cash;
        for lot in &self.lots {
            if let Some(&current_price) = current_prices.get(&lot.ticker) {
                total_balance += lot.shares * current_price;
            }
        }
        total_balance
    }
}

pub fn run_backtest(ctx: &Context) {
    let start_date = &ctx.config.start_date;
    let end_date = &ctx.config.end_date;
    let mut portfolio = ctx.portfolio.clone();

    println!("Start date:       {}", start_date);
    println!("End date:         {}", end_date);
    println!("Initial cash:     {:>10.2}", portfolio.cash);

    // Define constants for buy and sell prices
    const BUY_PRICE: f64 = 100.0;
    const SELL_PRICE: f64 = 110.0;
    let ticker = "ASSET";

    // Simulate buying the asset
    let shares_bought = portfolio.cash / BUY_PRICE;
    let lot = Lot {
        ticker: ticker.to_string(),
        shares: shares_bought,
        purchase_price: BUY_PRICE,
    };

    // Add the lot to the portfolio and update the cash balance
    portfolio.cash -= lot.shares * lot.purchase_price;
    portfolio.add_lot(lot);

    // Define current prices for assets
    let mut current_prices = HashMap::new();
    current_prices.insert(ticker.to_string(), SELL_PRICE);

    // Calculate the total balance after selling the asset
    let total_balance = portfolio.calculate_total_balance(&current_prices);

    println!("Ending cash:      {:>10.2}", portfolio.cash);
    println!("Ending balance:   {:>10.2}", total_balance);
    println!("Lots:             {:?}", portfolio.lots);
}
