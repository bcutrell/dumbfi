package finance

import "time"

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
