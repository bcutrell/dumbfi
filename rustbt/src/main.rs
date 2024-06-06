use clap::Parser;
use std::fs;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Cli {
    #[clap(short, long, value_parser)]
    config: String,
}

struct Context {
    config: Config,
}

fn main() {
    let cli = Cli::parse();

    // Read the configuration file
    let config_content =
        fs::read_to_string(cli.config).expect("Failed to read the configuration file");

    // Deserialize the configuration file
    let config: Config =
        toml::from_str(&config_content).expect("Failed to parse the configuration file");

    // init context
    let context = Context { config };

    // Run the backtest
    run_backtest(context);
}

fn run_backtest(ctx: Context) {
    println!("rustbt started");

    let start_date = &ctx.config.start_date;
    let end_date = &ctx.config.end_date;
    let balance = &ctx.config.initial_balance;

    println!("Start date: {}", start_date);
    println!("End date: {}", end_date);
    println!("Initial balance: {}", balance);

    // Add backtest logic here

    println!("Ending balance: {}", balance);

    println!("rustbt completed");
}

#[derive(Debug, serde::Deserialize)]
struct Config {
    start_date: String,
    end_date: String,
    initial_balance: f64,
}
