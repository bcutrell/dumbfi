package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	_ "github.com/joho/godotenv/autoload"
)

type StockPrice struct {
	Date          string  `json:"date"`
	Open          float64 `json:"open"`
	High          float64 `json:"high"`
	Low           float64 `json:"low"`
	Close         float64 `json:"close"`
	AdjustedClose float64 `json:"adjusted_close"`
	Volume        float64 `json:"volume"`
}

func main() {
	// Get API key from environment variable
	apiKey := os.Getenv("EODHD_API_KEY")
	if apiKey == "" {
		fmt.Println("Please set EODHD_API_KEY environment variable")
		return
	}

	symbols := []string{"SPY", "AAPL"}
	startDate := "2024-01-01"
	endDate := "2024-12-31"

	for _, symbol := range symbols {
		prices, err := fetchStockData(symbol, apiKey, startDate, endDate)
		if err != nil {
			fmt.Printf("Error fetching data for %s: %v\n", symbol, err)
			continue
		}
		formatPriceData(symbol, prices)
	}
}

// ---------------------------------------------------------------
// Prices
// ---------------------------------------------------------------

func fetchStockData(symbol string, apiKey string, startDate string, endDate string) ([]StockPrice, error) {
	if apiKey == "" {
		return nil, fmt.Errorf("API key is missing")
	}

	if err := validateDate(startDate); err != nil {
		return nil, fmt.Errorf("invalid startDate: %v", err)
	}
	if err := validateDate(endDate); err != nil {
		return nil, fmt.Errorf("invalid endDate: %v", err)
	}

	url := fmt.Sprintf("https://eodhd.com/api/eod/%s?from=%s&to=%s&api_token=%s&fmt=json",
		symbol, startDate, endDate, apiKey)

	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("error making request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API request failed with status %d: %s", resp.StatusCode, string(body))
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response: %v", err)
	}

	// Print the response body for debugging
	fmt.Println("Response Body:", string(body))

	var prices []StockPrice
	if err := json.Unmarshal(body, &prices); err != nil {
		return nil, fmt.Errorf("error parsing JSON: %v", err)
	}

	return prices, nil
}

func formatPriceData(symbol string, prices []StockPrice) {
	fmt.Printf("\nPrice data for %s:\n", symbol)
	fmt.Printf("%-12s %-10s %-10s %-10s %-10s %-10s\n",
		"Date", "Open", "High", "Low", "Close", "AdjustedClose")
	fmt.Println(strings.Repeat("-", 60))

	for _, price := range prices {
		fmt.Printf("%-12s $%-9.2f $%-9.2f $%-9.2f $%-9.2f $%-9.2f\n",
			price.Date, price.Open, price.High, price.Low,
			price.Close, price.AdjustedClose)
	}
}

func validateDate(date string) error {
	_, err := time.Parse("2006-01-02", date)
	if err != nil {
		return fmt.Errorf("must be YYYY-MM-DD format")
	}
	return nil
}
