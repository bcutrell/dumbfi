use clap::Parser;
use std::fs;
use rustbt::{Config, Context, Portfolio, run_backtest, read_prices};

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Path to the configuration file
    #[clap(short, long, value_parser)]
    config: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    let config_content = fs::read_to_string(cli.config)?;
    let config: Config = toml::from_str(&config_content)?;

    let prices = read_prices(&config.prices_file)?;

    let portfolio = Portfolio::new(config.init_cash);
    let context = Context { config, portfolio, prices };
    run_backtest(&context);

    Ok(())
}