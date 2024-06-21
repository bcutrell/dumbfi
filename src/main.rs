use clap::Parser;
use dumbfi::{run_backtest, Config, Context, MarketData, Portfolio};

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Path to the configuration file
    #[clap(short, long, required = true)]
    config: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    let config = Config::from_toml_file_path(&cli.config)?;

    let market_data = MarketData::new().with_prices_file(&config.prices_file)?;

    let portfolio = Portfolio::new(config.init_cash);
    let context = Context {
        config,
        portfolio,
        market_data,
    };
    run_backtest(&context);

    Ok(())
}
