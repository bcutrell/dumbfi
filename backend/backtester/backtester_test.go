package backtester

import (
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
)

func TestPortfolioCreation(t *testing.T) {
	assets := []Asset{
		{Symbol: "AAPL", Weight: 0.4},
		{Symbol: "MSFT", Weight: 0.3},
		{Symbol: "GOOG", Weight: 0.3},
	}
	targetWeights := map[string]float64{
		"AAPL": 0.4,
		"MSFT": 0.3,
		"GOOG": 0.3,
	}
	rebalancer := MonthlyRebalancer(targetWeights)
	portfolio := NewPortfolio(assets, 100000, 0.001, rebalancer)

	if portfolio.InitCash != 100000.0 {
		t.Errorf("Expected InitCash to be 100000.0, got %v", portfolio.InitCash)
	}
	if portfolio.Fees != 0.001 {
		t.Errorf("Expected Fees to be 0.001, got %v", portfolio.Fees)
	}
	if len(portfolio.Assets) != 3 {
		t.Errorf("Expected 3 assets, got %d", len(portfolio.Assets))
	}
	if portfolio.Assets[0].Symbol != "AAPL" {
		t.Errorf("Expected first asset to be AAPL, got %s", portfolio.Assets[0].Symbol)
	}
	if portfolio.Assets[0].Weight != 0.4 {
		t.Errorf("Expected AAPL weight to be 0.4, got %v", portfolio.Assets[0].Weight)
	}
}

func TestBacktestRun(t *testing.T) {
	assets := []Asset{
		{Symbol: "AAPL", Weight: 0.4},
		{Symbol: "MSFT", Weight: 0.3},
		{Symbol: "GOOG", Weight: 0.3},
	}
	assetSymbols := []string{"AAPL", "MSFT", "GOOG"}
	targetWeights := map[string]float64{
		"AAPL": 0.4,
		"MSFT": 0.3,
		"GOOG": 0.3,
	}
	rebalancer := MonthlyRebalancer(targetWeights)
	portfolio := NewPortfolio(assets, 100000, 0.001, rebalancer)
	startDate, _ := time.Parse("2006-01-02", "2020-01-01")
	endDate, _ := time.Parse("2006-01-02", "2020-12-31")
	priceData := GenerateDummyPriceData(assetSymbols, startDate, endDate)
	portfolio.SetPriceData(priceData)
	result, err := portfolio.Run()

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if result == nil {
		t.Fatal("Expected result to not be nil")
	}

	stats := result.Stats()
	if len(stats) == 0 {
		t.Error("Expected stats to not be empty")
	}
	if stats["final_value"] <= 0.0 {
		t.Errorf("Expected final_value > 0, got %v", stats["final_value"])
	}

	_, hasReturn := stats["total_return"]
	if !hasReturn {
		t.Error("Expected total_return to be present in stats")
	}

	_, hasVolatility := stats["volatility"]
	if !hasVolatility {
		t.Error("Expected volatility to be present in stats")
	}

	_, hasSharpe := stats["sharpe_ratio"]
	if !hasSharpe {
		t.Error("Expected sharpe_ratio to be present in stats")
	}
}

func TestMonthlyRebalancer(t *testing.T) {
	targetWeights := map[string]float64{
		"AAPL": 0.4,
		"MSFT": 0.3,
		"GOOG": 0.3,
	}
	rebalancer := MonthlyRebalancer(targetWeights)
	portfolio := &Portfolio{}

	endOfMonth, _ := time.Parse("2006-01-02", "2020-01-31")
	weights := rebalancer(portfolio, endOfMonth)

	if !cmp.Equal(targetWeights, weights) {
		t.Errorf("Expected weights %v, got %v", targetWeights, weights)
	}

	midMonth, _ := time.Parse("2006-01-02", "2020-01-15")
	weights = rebalancer(portfolio, midMonth)

	if weights != nil {
		t.Errorf("Expected nil weights for mid-month, got %v", weights)
	}
}

func TestGenerateDummyPriceData(t *testing.T) {
	assets := []string{"AAPL", "MSFT", "GOOG"}
	startDate, _ := time.Parse("2006-01-02", "2020-01-01")
	endDate, _ := time.Parse("2006-01-02", "2020-01-10")
	priceData := GenerateDummyPriceData(assets, startDate, endDate)

	if len(priceData.Dates) != 10 {
		t.Errorf("Expected 10 dates, got %d", len(priceData.Dates))
	}
	if len(priceData.Prices) != 3 {
		t.Errorf("Expected 3 price series, got %d", len(priceData.Prices))
	}

	for _, asset := range assets {
		prices, exists := priceData.Prices[asset]
		if !exists {
			t.Errorf("Expected to find prices for %s", asset)
			continue
		}

		for i, price := range prices {
			if price <= 0.0 {
				t.Errorf("Expected positive price for %s on day %d, got %v", asset, i, price)
			}
		}
	}
}

