package finance

import (
	"testing"
	"time"
)

func TestTaxLotValue(t *testing.T) {
	lot := TaxLot{
		Shares:    100,
		CostBasis: 50.0,
	}
	got := lot.Value(75.0)
	want := 7500.0
	if got != want {
		t.Errorf("TaxLot.Value() = %v, want %v", got, want)
	}
}

func TestTaxLotTotalCost(t *testing.T) {
	lot := TaxLot{
		Shares:    100,
		CostBasis: 50.0,
	}
	got := lot.TotalCost()
	want := 5000.0
	if got != want {
		t.Errorf("TaxLot.TotalCost() = %v, want %v", got, want)
	}
}

func TestHoldingWithMultipleLots(t *testing.T) {
	now := time.Now()
	holding := Holding{
		Ticker:       "VTI",
		TargetWeight: 0.6,
		Lots: []TaxLot{
			{Shares: 50, CostBasis: 100.0, PurchaseDate: now.AddDate(-2, 0, 0)},
			{Shares: 30, CostBasis: 120.0, PurchaseDate: now.AddDate(-1, 0, 0)},
		},
	}
	if holding.Ticker != "VTI" {
		t.Errorf("Holding.Ticker = %v, want VTI", holding.Ticker)
	}
	if len(holding.Lots) != 2 {
		t.Errorf("len(Holding.Lots) = %v, want 2", len(holding.Lots))
	}
}
