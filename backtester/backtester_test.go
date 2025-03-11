package backtester

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestPortfolioCreation(t *testing.T) {
	assets := []backtester.Asset{
		{Symbol: "AAPL", Weight: 0.4},
		{Symbol: "MSFT", Weight: 0.3},
		{Symbol: "GOOG", Weight: 0.3},
	}

	targetWeights := map[string]float64{
		"AAPL": 0.4,
		"MSFT": 0.3,
		"GOOG": 0.3,
	}

	rebalancer := backtester.MonthlyRebalancer(targetWeights)

	portfolio := backtester.NewPortfolio(assets, 100000, 0.001, rebalancer)

	assert.Equal(t, 100000.0, portfolio.InitCash)
	assert.Equal(t, 0.001, portfolio.Fees)
	assert.Equal(t, 3, len(portfolio.Assets))
	assert.Equal(t, "AAPL", portfolio.Assets[0].Symbol)
	assert.Equal(t, 0.4, portfolio.Assets[0].Weight)
}

func TestBacktestRun(t *testing.T) {
	assets := []backtester.Asset{
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

	rebalancer := backtester.MonthlyRebalancer(targetWeights)

	portfolio := backtester.NewPortfolio(assets, 100000, 0.001, rebalancer)

	startDate, _ := time.Parse("2006-01-02", "2020-01-01")
	endDate, _ := time.Parse("2006-01-02", "2020-12-31")
	priceData := backtester.GenerateDummyPriceData(assetSymbols, startDate, endDate)

	portfolio.SetPriceData(priceData)

	result, err := portfolio.Run()

	assert.Nil(t, err)
	assert.NotNil(t, result)

	stats := result.Stats()
	assert.NotEmpty(t, stats)

	assert.Greater(t, stats["final_value"], 0.0)

	_, hasReturn := stats["total_return"]
	assert.True(t, hasReturn)

	_, hasVolatility := stats["volatility"]
	assert.True(t, hasVolatility)

	_, hasSharpe := stats["sharpe_ratio"]
	assert.True(t, hasSharpe)
}

func TestMonthlyRebalancer(t *testing.T) {
	targetWeights := map[string]float64{
		"AAPL": 0.4,
		"MSFT": 0.3,
		"GOOG": 0.3,
	}

	rebalancer := backtester.MonthlyRebalancer(targetWeights)

	portfolio := &backtester.Portfolio{}

	endOfMonth, _ := time.Parse("2006-01-02", "2020-01-31")
	weights := rebalancer(portfolio, endOfMonth)
	assert.Equal(t, targetWeights, weights)

	midMonth, _ := time.Parse("2006-01-02", "2020-01-15")
	weights = rebalancer(portfolio, midMonth)
	assert.Nil(t, weights)
}

func TestGenerateDummyPriceData(t *testing.T) {
	assets := []string{"AAPL", "MSFT", "GOOG"}
	startDate, _ := time.Parse("2006-01-02", "2020-01-01")
	endDate, _ := time.Parse("2006-01-02", "2020-01-10")

	priceData := backtester.GenerateDummyPriceData(assets, startDate, endDate)

	assert.Equal(t, 10, len(priceData.Dates))
	assert.Equal(t, 3, len(priceData.Prices))

	assert.Contains(t, priceData.Prices, "AAPL")
	assert.Contains(t, priceData.Prices, "MSFT")
	assert.Contains(t, priceData.Prices, "GOOG")

	for _, asset := range assets {
		for i := 0; i < len(priceData.Dates); i++ {
			price := priceData.Prices[asset][i]
			assert.Greater(t, price, 0.0)
		}
	}
}
