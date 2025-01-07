package main

// TODO
// [] Add a function for getting multiple symbols
// [] Have an object that takes EOD API key and has a function for getting prices

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

type EODClient struct {
	apiKey     string
	httpClient *http.Client
}

// ---------------------------------------------------------------
// Prices
// ---------------------------------------------------------------

func NewEODClient(apiKey string) *EODClient {
	return &EODClient{
		apiKey: apiKey,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (c *EODClient) GetPrices(symbols []string, startDate, endDate string) (map[string][]StockPrice, error) {
	if err := c.validateInput(symbols, startDate, endDate); err != nil {
		return nil, err
	}

	results := make(map[string][]StockPrice)
	errorChan := make(chan error, len(symbols))
	resultChan := make(chan struct {
		symbol string
		prices []StockPrice
		err    error
	}, len(symbols))

	// Fetch prices concurrently
	for _, symbol := range symbols {
		go func(sym string) {
			prices, err := c.fetchEOD(sym, startDate, endDate)
			resultChan <- struct {
				symbol string
				prices []StockPrice
				err    error
			}{sym, prices, err}
		}(symbol)
	}

	// Collect results
	for range symbols {
		result := <-resultChan
		if result.err != nil {
			errorChan <- fmt.Errorf("error fetching data for %s: %v", result.symbol, result.err)
			continue
		}
		results[result.symbol] = result.prices
	}

	// Check for any errors
	select {
	case err := <-errorChan:
		return nil, err
	default:
		return results, nil
	}
}

func (c *EODClient) validateInput(symbols []string, startDate, endDate string) error {
	if len(symbols) == 0 {
		return fmt.Errorf("no symbols provided")
	}

	if c.apiKey == "" {
		return fmt.Errorf("API key is missing")
	}

	if err := validateDate(startDate); err != nil {
		return fmt.Errorf("invalid startDate: %v", err)
	}
	if err := validateDate(endDate); err != nil {
		return fmt.Errorf("invalid endDate: %v", err)
	}

	return nil
}

func (c *EODClient) fetchEOD(symbol, startDate, endDate string) ([]StockPrice, error) {
	url := fmt.Sprintf("https://eodhd.com/api/eod/%s?from=%s&to=%s&api_token=%s&fmt=json",
		symbol, startDate, endDate, c.apiKey)

	resp, err := c.httpClient.Get(url)
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

	var prices []StockPrice
	if err := json.Unmarshal(body, &prices); err != nil {
		return nil, fmt.Errorf("error parsing JSON: %v", err)
	}

	return prices, nil
}

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

func main() {
	apiKey := os.Getenv("EODHD_API_KEY")
	if apiKey == "" {
		fmt.Println("Please set EODHD_API_KEY environment variable")
		return
	}

	client := NewEODClient(apiKey)
	symbols := []string{"SPY", "AAPL", "MSFT"}
	startDate := "2024-01-01"
	endDate := "2024-12-31"

	results, err := client.GetPrices(symbols, startDate, endDate)
	if err != nil {
		fmt.Printf("Error fetching prices: %v\n", err)
		return
	}

	for symbol, prices := range results {
		formatPriceData(symbol, prices)
	}
}
