// Backtest CLI - Run backtesting simulations on historical data.
package main

import (
	"flag"
	"fmt"

	"github.com/bcutrell/dumbfi/go/finance"
)

func main() {
	dataFile := flag.String("data", "../data/prices.csv", "Path to price data CSV")
	strategy := flag.String("strategy", "momentum", "Strategy to backtest")
	startDate := flag.String("start", "2024-01-01", "Start date")
	endDate := flag.String("end", "2024-12-31", "End date")
	flag.Parse()

	fmt.Println("DumbFi Backtester")
	fmt.Println("=================")
	fmt.Printf("Data file: %s\n", *dataFile)
	fmt.Printf("Strategy: %s\n", *strategy)
	fmt.Printf("Period: %s to %s\n", *startDate, *endDate)

	// Load market data
	market := finance.NewMarketData()
	err := market.LoadFromCSV(*dataFile)
	if err != nil {
		fmt.Printf("Error loading data: %v\n", err)
		return
	}

	fmt.Printf("Loaded %d dates, %d tickers\n",
		len(market.GetAvailableDates()),
		len(market.GetAvailableTickers()))

	// TODO: Implement backtesting logic
	fmt.Println("\nBacktesting not yet implemented. Coming soon!")
}
