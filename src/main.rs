use clap::Parser;
use dumbfi::{run_backtest, Config, Context, MarketData, Portfolio};
use std::fs;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Path to the configuration file
    #[clap(short, long, required = true)]
    config: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    let config_content = fs::read_to_string(cli.config)?;
    let config: Config = toml::from_str(&config_content)?;

    let market_data = MarketData::new();
    market_data.load_prices_from_csv(&config.prices_file)?;

    let portfolio = Portfolio::new(config.init_cash);
    let context = Context {
        config,
        portfolio,
        market_data,
    };
    run_backtest(&context);

    Ok(())
}
