package finance

import (
	"math"
	"sort"
	"time"
)

// Optimizer provides portfolio optimization functionality.
// TODO: Implement using gonum for matrix operations.
type Optimizer struct {
	ExpectedReturns []float64
	CovMatrix       [][]float64
	Tickers         []string
}

// NewOptimizer creates a new portfolio optimizer.
func NewOptimizer(returns []float64, cov [][]float64, tickers []string) *Optimizer {
	return &Optimizer{
		ExpectedReturns: returns,
		CovMatrix:       cov,
		Tickers:         tickers,
	}
}

// OptimizationResult holds the result of a portfolio optimization.
type OptimizationResult struct {
	Weights        map[string]float64
	ExpectedReturn float64
	Volatility     float64
	SharpeRatio    float64
}

// MaxSharpe finds the portfolio with maximum Sharpe ratio.
// TODO: Implement optimization using gonum.
func (o *Optimizer) MaxSharpe(riskFreeRate float64) (*OptimizationResult, error) {
	// Placeholder - to be implemented
	result := &OptimizationResult{
		Weights: make(map[string]float64),
	}
	// Equal weight as placeholder
	for _, ticker := range o.Tickers {
		result.Weights[ticker] = 1.0 / float64(len(o.Tickers))
	}
	return result, nil
}

// MinVolatility finds the minimum volatility portfolio.
// TODO: Implement optimization using gonum.
func (o *Optimizer) MinVolatility() (*OptimizationResult, error) {
	// Placeholder - to be implemented
	result := &OptimizationResult{
		Weights: make(map[string]float64),
	}
	// Equal weight as placeholder
	for _, ticker := range o.Tickers {
		result.Weights[ticker] = 1.0 / float64(len(o.Tickers))
	}
	return result, nil
}

//
// Tax Aware
//

type Holding struct {
	Ticker       string
	TargetWeight float64
	Lots         []TaxLot
}

type TaxLot struct {
	Shares       float64
	CostBasis    float64 // per share
	PurchaseDate time.Time
}

func (lot TaxLot) Value(price float64) float64 {
	return lot.Shares * price
}

func (lot TaxLot) TotalCost() float64 {
	return lot.Shares * lot.CostBasis
}

func HoldingValue(h Holding, price float64) float64 {
	var total float64
	for _, lot := range h.Lots {
		total += lot.Value(price)
	}
	return total
}

func PortfolioValue(holdings []Holding, prices map[string]float64) float64 {
	var total float64
	for _, h := range holdings {
		if price, ok := prices[h.Ticker]; ok {
			total += HoldingValue(h, price)
		}
	}
	return total
}

func CurrentWeights(holdings []Holding, prices map[string]float64) map[string]float64 {
	total := PortfolioValue(holdings, prices)
	weights := make(map[string]float64)
	if total == 0 {
		return weights
	}
	for _, h := range holdings {
		if price, ok := prices[h.Ticker]; ok {
			weights[h.Ticker] = HoldingValue(h, price) / total
		}
	}
	return weights
}

// Drift returns current weight minus target weight for each holding.
func Drift(holdings []Holding, prices map[string]float64) map[string]float64 {
	current := CurrentWeights(holdings, prices)
	drift := make(map[string]float64)
	for _, h := range holdings {
		drift[h.Ticker] = current[h.Ticker] - h.TargetWeight
	}
	return drift
}

// DriftCost returns sum of squared drifts.
func DriftCost(holdings []Holding, prices map[string]float64) float64 {
	drift := Drift(holdings, prices)
	var cost float64
	for _, d := range drift {
		cost += d * d
	}
	return cost
}

// LotSelector orders lots for selling. Returns a copy sorted by selection priority.
type LotSelector func(lots []TaxLot) []TaxLot

// FIFO returns lots ordered by purchase date (oldest first).
func FIFO(lots []TaxLot) []TaxLot {
	sorted := make([]TaxLot, len(lots))
	copy(sorted, lots)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].PurchaseDate.Before(sorted[j].PurchaseDate)
	})
	return sorted
}

// LIFO returns lots ordered by purchase date (newest first).
func LIFO(lots []TaxLot) []TaxLot {
	sorted := make([]TaxLot, len(lots))
	copy(sorted, lots)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].PurchaseDate.After(sorted[j].PurchaseDate)
	})
	return sorted
}

// HighestCostFirst returns lots ordered by cost basis (highest first).
func HighestCostFirst(lots []TaxLot) []TaxLot {
	sorted := make([]TaxLot, len(lots))
	copy(sorted, lots)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].CostBasis > sorted[j].CostBasis
	})
	return sorted
}

// UnrealizedGain returns the gain (positive) or loss (negative) for a lot.
func UnrealizedGain(lot TaxLot, price float64) float64 {
	return lot.Value(price) - lot.TotalCost()
}

// IsLongTerm returns true if the lot has been held for more than 1 year.
func IsLongTerm(lot TaxLot, asOf time.Time) bool {
	return asOf.Sub(lot.PurchaseDate) > 365*24*time.Hour
}

// TaxRates holds long-term and short-term capital gains tax rates.
type TaxRates struct {
	ShortTerm float64
	LongTerm  float64
}

// DefaultTaxRates returns typical US federal tax rates.
func DefaultTaxRates() TaxRates {
	return TaxRates{ShortTerm: 0.35, LongTerm: 0.15}
}

// TaxCost estimates the tax impact of selling a lot. Positive = tax owed, negative = tax benefit.
func TaxCost(lot TaxLot, price float64, asOf time.Time, rates TaxRates) float64 {
	gain := UnrealizedGain(lot, price)
	if IsLongTerm(lot, asOf) {
		return gain * rates.LongTerm
	}
	return gain * rates.ShortTerm
}

// RebalanceConfig controls the rebalancing behavior.
type RebalanceConfig struct {
	TaxRates     TaxRates
	LotSelector  LotSelector
	AsOf         time.Time
	MinTradeSize float64 // minimum dollar amount to trigger a trade
}

// Trade represents a buy or sell action.
type Trade struct {
	Ticker  string
	Shares  float64 // positive = buy, negative = sell
	Amount  float64 // dollar value (positive = buy, negative = sell)
	TaxCost float64 // estimated tax impact (only for sells)
}

// Rebalance generates trades to move holdings toward target weights.
func Rebalance(holdings []Holding, prices map[string]float64, config RebalanceConfig) []Trade {
	total := PortfolioValue(holdings, prices)
	if total == 0 {
		return nil
	}

	var trades []Trade
	for _, h := range holdings {
		price := prices[h.Ticker]
		currentValue := HoldingValue(h, price)
		targetValue := total * h.TargetWeight
		diff := targetValue - currentValue

		if math.Abs(diff) < config.MinTradeSize {
			continue
		}

		if diff > 0 {
			// Buy
			shares := diff / price
			trades = append(trades, Trade{
				Ticker: h.Ticker,
				Shares: shares,
				Amount: diff,
			})
		} else {
			// Sell
			sellAmount := -diff
			sellShares := sellAmount / price
			taxCost := calculateSellTaxCost(h, price, sellShares, config)
			trades = append(trades, Trade{
				Ticker:  h.Ticker,
				Shares:  -sellShares,
				Amount:  -sellAmount,
				TaxCost: taxCost,
			})
		}
	}
	return trades
}

func calculateSellTaxCost(h Holding, price, sharesToSell float64, config RebalanceConfig) float64 {
	sortedLots := config.LotSelector(h.Lots)
	var totalTax float64
	remaining := sharesToSell

	for _, lot := range sortedLots {
		if remaining <= 0 {
			break
		}
		sellFromLot := lot.Shares
		if sellFromLot > remaining {
			sellFromLot = remaining
		}
		partialLot := TaxLot{
			Shares:       sellFromLot,
			CostBasis:    lot.CostBasis,
			PurchaseDate: lot.PurchaseDate,
		}
		totalTax += TaxCost(partialLot, price, config.AsOf, config.TaxRates)
		remaining -= sellFromLot
	}
	return totalTax
}

// TotalTaxCost sums the tax cost across all trades.
func TotalTaxCost(trades []Trade) float64 {
	var total float64
	for _, t := range trades {
		total += t.TaxCost
	}
	return total
}
