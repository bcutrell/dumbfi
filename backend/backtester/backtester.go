package backtester

import (
	"fmt"
	"math"
	"math/rand"
	"time"
)

type Asset struct {
	Symbol string
	Weight float64
}

type PriceData struct {
	Dates  []time.Time
	Prices map[string][]float64
}

type Portfolio struct {
	Assets     []Asset
	InitCash   float64
	Fees       float64
	PriceData  PriceData
	Holdings   map[string]float64
	Cash       []float64
	Value      []float64
	Weights    []map[string]float64
	Dates      []time.Time
	Rebalancer RebalancerFunc
}

type RebalancerFunc func(p *Portfolio, date time.Time) map[string]float64

type BacktestResult struct {
	Portfolio *Portfolio
}

func NewPortfolio(assets []Asset, initialCash float64, fees float64, rebalancer RebalancerFunc) *Portfolio {
	weights := make(map[string]float64)
	holdings := make(map[string]float64)

	for _, asset := range assets {
		weights[asset.Symbol] = asset.Weight
		holdings[asset.Symbol] = 0
	}

	return &Portfolio{
		Assets:     assets,
		InitCash:   initialCash,
		Fees:       fees,
		Cash:       []float64{initialCash},
		Value:      []float64{initialCash},
		Weights:    []map[string]float64{weights},
		Holdings:   holdings,
		Dates:      []time.Time{},
		Rebalancer: rebalancer,
	}
}

func MonthlyRebalancer(targetWeights map[string]float64) RebalancerFunc {
	return func(p *Portfolio, date time.Time) map[string]float64 {
		nextDay := date.AddDate(0, 0, 1)
		if nextDay.Month() != date.Month() {
			return targetWeights
		}
		return nil
	}
}

func (p *Portfolio) SetPriceData(priceData PriceData) {
	p.PriceData = priceData
}

func (p *Portfolio) Run() (*BacktestResult, error) {
	if len(p.PriceData.Dates) == 0 {
		return nil, fmt.Errorf("price data is empty")
	}

	currCash := p.InitCash
	currHoldings := make(map[string]float64)
	for _, asset := range p.Assets {
		currHoldings[asset.Symbol] = 0
	}

	values := []float64{p.InitCash}
	cashValues := []float64{p.InitCash}
	allWeights := []map[string]float64{p.Weights[0]}
	dates := []time.Time{}

	for i, date := range p.PriceData.Dates {
		rebWeights := p.Rebalancer(p, date)

		if rebWeights != nil {
			portfolioValue := currCash
			for symbol, qty := range currHoldings {
				price := p.PriceData.Prices[symbol][i]
				portfolioValue += qty * price
			}

			targetPositions := make(map[string]float64)
			for symbol, weight := range rebWeights {
				targetPositions[symbol] = portfolioValue * weight / p.PriceData.Prices[symbol][i]
			}

			for symbol, targetQty := range targetPositions {
				currentQty := currHoldings[symbol]
				diffQty := targetQty - currentQty

				if diffQty != 0 {
					price := p.PriceData.Prices[symbol][i]
					tradeCost := price * diffQty
					feeCost := p.Fees * math.Abs(tradeCost)

					currCash -= (tradeCost + feeCost)
					currHoldings[symbol] = targetQty
				}
			}
		}

		totalValue := currCash
		weights := make(map[string]float64)
		for symbol, qty := range currHoldings {
			price := p.PriceData.Prices[symbol][i]
			assetValue := qty * price
			totalValue += assetValue
			weights[symbol] = assetValue / totalValue
		}

		values = append(values, totalValue)
		cashValues = append(cashValues, currCash)
		allWeights = append(allWeights, weights)
		dates = append(dates, date)
	}

	p.Value = values
	p.Cash = cashValues
	p.Weights = allWeights
	p.Dates = dates

	return &BacktestResult{
		Portfolio: p,
	}, nil
}

func (r *BacktestResult) Stats() map[string]float64 {
	if len(r.Portfolio.Value) < 2 {
		return map[string]float64{}
	}

	initialValue := r.Portfolio.Value[0]
	finalValue := r.Portfolio.Value[len(r.Portfolio.Value)-1]
	returns := finalValue/initialValue - 1

	years := float64(len(r.Portfolio.Dates)) / 252
	annReturn := math.Pow(1+returns, 1/years) - 1

	dailyReturns := make([]float64, len(r.Portfolio.Value)-1)
	for i := 1; i < len(r.Portfolio.Value); i++ {
		dailyReturns[i-1] = r.Portfolio.Value[i]/r.Portfolio.Value[i-1] - 1
	}
	volatility := calcStdDev(dailyReturns) * math.Sqrt(252)

	maxDrawdown := calcMaxDrawdown(r.Portfolio.Value)

	sharpeRatio := annReturn / volatility

	return map[string]float64{
		"total_return":      returns * 100,
		"annualized_return": annReturn * 100,
		"volatility":        volatility * 100,
		"sharpe_ratio":      sharpeRatio,
		"max_drawdown":      maxDrawdown * 100,
		"final_value":       finalValue,
	}
}

func calcStdDev(data []float64) float64 {
	if len(data) == 0 {
		return 0
	}

	sum := 0.0
	for _, v := range data {
		sum += v
	}
	mean := sum / float64(len(data))

	variance := 0.0
	for _, v := range data {
		variance += (v - mean) * (v - mean)
	}
	variance /= float64(len(data))

	return math.Sqrt(variance)
}

func calcMaxDrawdown(values []float64) float64 {
	if len(values) < 2 {
		return 0
	}

	maxDrawdown := 0.0
	peak := values[0]

	for _, value := range values {
		if value > peak {
			peak = value
		}

		drawdown := (peak - value) / peak
		if drawdown > maxDrawdown {
			maxDrawdown = drawdown
		}
	}

	return maxDrawdown
}

func GenerateDummyPriceData(assets []string, startDate, endDate time.Time) PriceData {
	rand.Seed(42)

	var dates []time.Time
	for d := startDate; !d.After(endDate); d = d.AddDate(0, 0, 1) {
		dates = append(dates, d)
	}

	priceMap := make(map[string][]float64)
	for _, asset := range assets {
		prices := make([]float64, len(dates))
		prices[0] = 100

		for i := 1; i < len(dates); i++ {
			dailyReturn := rand.NormFloat64()*0.01 + 0.0001
			prices[i] = prices[i-1] * (1 + dailyReturn)
		}

		priceMap[asset] = prices
	}

	return PriceData{
		Dates:  dates,
		Prices: priceMap,
	}
}
