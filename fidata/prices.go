package main

import (
	"encoding/json"
	"fmt"
	_ "github.com/joho/godotenv/autoload"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

type StockPrice struct {
	Date           string  `json:"date"`
	Open           float64 `json:"open"`
	High           float64 `json:"high"`
	Low            float64 `json:"low"`
	Close          float64 `json:"close"`
	Adjusted_close float64 `json:"adjusted_close"`
	Volume         float64 `json:"volume"`
}

func fetchStockData(symbol string, apiKey string) ([]StockPrice, error) {
	// Get start date as January 1, 2024
	startDate := "2024-01-01"
	// Get current date
	endDate := time.Now().Format("2006-01-02")

	url := fmt.Sprintf("https://eodhd.com/api/eod/%s?from=%s&to=%s&api_token=%s&fmt=json",
		symbol, startDate, endDate, apiKey)

	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("error making request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response: %v", err)
	}

	var prices []StockPrice
	if err := json.Unmarshal(body, &prices); err != nil {
		return nil, fmt.Errorf("error parsing JSON: %v", err)
	}

	return prices, nil
}

func main() {
	// Get API key from environment variable
	apiKey := os.Getenv("EODHD_API_KEY")
	if apiKey == "" {
		fmt.Println("Please set EODHD_API_KEY environment variable")
		return
	}

	symbols := []string{"SPY", "AAPL"}

	for _, symbol := range symbols {
		prices, err := fetchStockData(symbol, apiKey)
		if err != nil {
			fmt.Printf("Error fetching data for %s: %v\n", symbol, err)
			continue
		}

		fmt.Printf("\nPrice data for %s:\n", symbol)
		fmt.Printf("%-12s %-10s %-10s %-10s %-10s %-10s\n", "Date", "Open", "High", "Low", "Close", "Adjusted_close")
		fmt.Println(strings.Repeat("-", 60))

		for _, price := range prices {
			fmt.Printf("%-12s $%-9.2f $%-9.2f $%-9.2f $%-9.2f $%-9.2f\n",
				price.Date, price.Open, price.High, price.Low, price.Close, price.Adjusted_close)
		}
	}
}
