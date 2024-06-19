use dumbfi::{Config, Lot, Portfolio};
use std::collections::HashMap;

#[test]
fn test_portfolio_initialization() {
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
