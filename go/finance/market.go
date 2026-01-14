package finance

import (
	"encoding/csv"
	"os"
	"strconv"
)

// MarketData holds price data for multiple assets across dates.
type MarketData struct {
	prices  map[string]map[string]float64 // date -> ticker -> price
	tickers []string
	dates   []string
}

// NewMarketData creates an empty MarketData instance.
func NewMarketData() *MarketData {
	return &MarketData{
		prices:  make(map[string]map[string]float64),
		tickers: []string{},
		dates:   []string{},
	}
}

// LoadFromCSV loads market data from a CSV file.
// Expected format: Date,TICKER1,TICKER2,...
func (m *MarketData) LoadFromCSV(filepath string) error {
	file, err := os.Open(filepath)
	if err != nil {
		return err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return err
	}

	if len(records) < 2 {
		return nil // Empty file
	}

	// Header row contains tickers
	header := records[0]
	m.tickers = header[1:] // Skip "Date" column

	// Process data rows
	for _, row := range records[1:] {
		date := row[0]
		m.dates = append(m.dates, date)
		m.prices[date] = make(map[string]float64)

		for i, ticker := range m.tickers {
			if i+1 < len(row) {
				price, err := strconv.ParseFloat(row[i+1], 64)
				if err == nil {
					m.prices[date][ticker] = price
				}
			}
		}
	}

	return nil
}

// GetPrice returns the price for a ticker on a given date.
func (m *MarketData) GetPrice(date, ticker string) (float64, bool) {
	if dateData, ok := m.prices[date]; ok {
		if price, ok := dateData[ticker]; ok {
			return price, true
		}
	}
	return 0, false
}

// GetAvailableDates returns all available dates.
func (m *MarketData) GetAvailableDates() []string {
	return m.dates
}

// GetAvailableTickers returns all available tickers.
func (m *MarketData) GetAvailableTickers() []string {
	return m.tickers
}
