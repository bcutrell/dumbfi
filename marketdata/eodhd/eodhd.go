package eodhd

import (
	"encoding/json"
	"fmt"
	"github.com/bcutrell/dumbfi/utils"
	"io"
	"net/http"
	"time"
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

type Client struct {
	apiKey     string
	httpClient *http.Client
}

func NewClient(apiKey string) *Client {
	return &Client{
		apiKey: apiKey,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (c *Client) validateInput(symbols []string, startDate, endDate string) error {
	if len(symbols) == 0 {
		return fmt.Errorf("no symbols provided")
	}

	if c.apiKey == "" {
		return fmt.Errorf("API key is missing")
	}

	if err := utils.ValidateDate(startDate); err != nil {
		return fmt.Errorf("invalid startDate: %v", err)
	}
	if err := utils.ValidateDate(endDate); err != nil {
		return fmt.Errorf("invalid endDate: %v", err)
	}

	return nil
}

func (c *Client) GetPrices(symbols []string, startDate, endDate string) (map[string][]StockPrice, error) {
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
			prices, err := c.fetchAndUnmarshal(sym, startDate, endDate)
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

func (c *Client) fetchAndUnmarshal(symbol, startDate, endDate string) ([]StockPrice, error) {
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
