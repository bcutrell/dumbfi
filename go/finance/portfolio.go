// Package finance provides core financial data structures and operations.
package finance

// Position represents a single stock position.
type Position struct {
	Ticker       string
	Quantity     float64
	AvgCost      float64
	CurrentPrice float64
}

// MarketValue returns the current market value of the position.
func (p *Position) MarketValue() float64 {
	return p.Quantity * p.CurrentPrice
}

// CostBasis returns the total cost basis of the position.
func (p *Position) CostBasis() float64 {
	return p.Quantity * p.AvgCost
}

// UnrealizedPnL returns the unrealized profit/loss.
func (p *Position) UnrealizedPnL() float64 {
	return p.MarketValue() - p.CostBasis()
}

// Portfolio represents a collection of positions with cash.
type Portfolio struct {
	Name        string
	Cash        float64
	Positions   map[string]*Position
	InitialCash float64
}

// NewPortfolio creates a new portfolio with the given initial cash.
func NewPortfolio(initialCash float64, name string) *Portfolio {
	return &Portfolio{
		Name:        name,
		Cash:        initialCash,
		Positions:   make(map[string]*Position),
		InitialCash: initialCash,
	}
}

// TotalValue returns the total portfolio value (cash + positions).
func (p *Portfolio) TotalValue() float64 {
	total := p.Cash
	for _, pos := range p.Positions {
		total += pos.MarketValue()
	}
	return total
}

// TotalReturn returns the total return as a percentage.
func (p *Portfolio) TotalReturn() float64 {
	if p.InitialCash == 0 {
		return 0
	}
	return (p.TotalValue() - p.InitialCash) / p.InitialCash * 100
}
