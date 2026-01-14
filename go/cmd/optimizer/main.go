// Optimizer CLI - Portfolio optimization tool.
package main

import (
	"flag"
	"fmt"

	"github.com/bcutrell/dumbfi/go/finance"
)

func main() {
	dataFile := flag.String("data", "../data/prices.csv", "Path to price data CSV")
	targetReturn := flag.Float64("target-return", 0.12, "Target annual return")
	method := flag.String("method", "max-sharpe", "Optimization method")
	flag.Parse()

	fmt.Println("DumbFi Portfolio Optimizer")
	fmt.Println("==========================")
	fmt.Printf("Data file: %s\n", *dataFile)
	fmt.Printf("Method: %s\n", *method)
	fmt.Printf("Target return: %.1f%%\n", *targetReturn*100)

	// Load market data
	market := finance.NewMarketData()
	err := market.LoadFromCSV(*dataFile)
	if err != nil {
		fmt.Printf("Error loading data: %v\n", err)
		return
	}

	fmt.Printf("Loaded %d tickers\n", len(market.GetAvailableTickers()))

	// TODO: Calculate returns and covariance
	// TODO: Run optimization
	fmt.Println("\nOptimization not yet implemented. Coming soon!")
}
