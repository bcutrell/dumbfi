use std::collections::HashMap;
use chrono::NaiveDate;
use std::error::Error;
use std::fs::File;
use std::io::BufReader;
use csv::ReaderBuilder;

#[derive(Debug, serde::Deserialize)]
pub struct Config {
    pub start_date: String,
    pub end_date: String,
    pub init_cash: f64,
    pub prices_file: String,
}

pub type Ticker = String;
pub type Date = NaiveDate;
pub type Price = f64;
type Prices = HashMap<Ticker, HashMap<Date, Price>>;

pub struct Context {
    pub config: Config,
    pub portfolio: Portfolio,
    pub prices: Prices,
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

pub fn read_prices(file_path: &str) -> Result<Prices, Box<dyn Error>> {
    let file = File::open(file_path)?;
    let reader = BufReader::new(file);
    let mut csv_reader = ReaderBuilder::new().from_reader(reader);

    let mut prices: Prices = HashMap::new();

    for result in csv_reader.records() {
        let record = result?;
        let ticker: Ticker = record[0].to_string();
        let date: Date = NaiveDate::parse_from_str(&record[1], "%Y-%m-%d")?;
        let price: Price = record[2].parse()?;

        prices
            .entry(ticker)
            .or_insert_with(HashMap::new)
            .insert(date, price);
    }

    Ok(prices)
}

pub fn run_backtest(ctx: &Context) {
    println!("dumbbt started");

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
    println!("dumbbt completed");
}