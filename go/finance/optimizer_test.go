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

func TestHoldingValue(t *testing.T) {
	h := Holding{
		Ticker: "VTI",
		Lots: []TaxLot{
			{Shares: 100, CostBasis: 50.0},
			{Shares: 50, CostBasis: 60.0},
		},
	}
	got := HoldingValue(h, 75.0)
	want := 11250.0 // (100 + 50) * 75
	if got != want {
		t.Errorf("HoldingValue() = %v, want %v", got, want)
	}
}

func TestPortfolioValue(t *testing.T) {
	holdings := []Holding{
		{Ticker: "VTI", Lots: []TaxLot{{Shares: 100, CostBasis: 50.0}}},
		{Ticker: "BND", Lots: []TaxLot{{Shares: 200, CostBasis: 40.0}}},
	}
	prices := map[string]float64{"VTI": 75.0, "BND": 50.0}
	got := PortfolioValue(holdings, prices)
	want := 17500.0 // 100*75 + 200*50
	if got != want {
		t.Errorf("PortfolioValue() = %v, want %v", got, want)
	}
}

func TestCurrentWeights(t *testing.T) {
	holdings := []Holding{
		{Ticker: "VTI", Lots: []TaxLot{{Shares: 100, CostBasis: 50.0}}},
		{Ticker: "BND", Lots: []TaxLot{{Shares: 200, CostBasis: 40.0}}},
	}
	prices := map[string]float64{"VTI": 75.0, "BND": 50.0}
	weights := CurrentWeights(holdings, prices)
	// VTI: 7500/17500 = 0.4286, BND: 10000/17500 = 0.5714
	if w := weights["VTI"]; w < 0.42 || w > 0.43 {
		t.Errorf("CurrentWeights()[VTI] = %v, want ~0.4286", w)
	}
	if w := weights["BND"]; w < 0.57 || w > 0.58 {
		t.Errorf("CurrentWeights()[BND] = %v, want ~0.5714", w)
	}
}

func TestCurrentWeightsEmpty(t *testing.T) {
	weights := CurrentWeights([]Holding{}, map[string]float64{})
	if len(weights) != 0 {
		t.Errorf("CurrentWeights([]) should return empty map")
	}
}

func TestDrift(t *testing.T) {
	holdings := []Holding{
		{Ticker: "VTI", TargetWeight: 0.6, Lots: []TaxLot{{Shares: 100, CostBasis: 50.0}}},
		{Ticker: "BND", TargetWeight: 0.4, Lots: []TaxLot{{Shares: 200, CostBasis: 40.0}}},
	}
	prices := map[string]float64{"VTI": 75.0, "BND": 50.0}
	// VTI current: 0.4286, target: 0.6, drift: -0.1714
	// BND current: 0.5714, target: 0.4, drift: +0.1714
	drift := Drift(holdings, prices)
	if d := drift["VTI"]; d > -0.17 || d < -0.18 {
		t.Errorf("Drift[VTI] = %v, want ~-0.1714", d)
	}
	if d := drift["BND"]; d < 0.17 || d > 0.18 {
		t.Errorf("Drift[BND] = %v, want ~+0.1714", d)
	}
}

func TestDriftCost(t *testing.T) {
	holdings := []Holding{
		{Ticker: "VTI", TargetWeight: 0.6, Lots: []TaxLot{{Shares: 100, CostBasis: 50.0}}},
		{Ticker: "BND", TargetWeight: 0.4, Lots: []TaxLot{{Shares: 200, CostBasis: 40.0}}},
	}
	prices := map[string]float64{"VTI": 75.0, "BND": 50.0}
	// Drift: VTI=-0.1714, BND=+0.1714
	// Cost: 0.1714^2 + 0.1714^2 = 0.0588
	cost := DriftCost(holdings, prices)
	if cost < 0.058 || cost > 0.060 {
		t.Errorf("DriftCost() = %v, want ~0.0588", cost)
	}
}

func TestDriftCostZeroWhenBalanced(t *testing.T) {
	holdings := []Holding{
		{Ticker: "VTI", TargetWeight: 0.6, Lots: []TaxLot{{Shares: 60, CostBasis: 100.0}}},
		{Ticker: "BND", TargetWeight: 0.4, Lots: []TaxLot{{Shares: 40, CostBasis: 100.0}}},
	}
	prices := map[string]float64{"VTI": 100.0, "BND": 100.0}
	cost := DriftCost(holdings, prices)
	if cost > 0.0001 {
		t.Errorf("DriftCost() = %v, want ~0 when balanced", cost)
	}
}

func makeLots() []TaxLot {
	now := time.Now()
	return []TaxLot{
		{Shares: 10, CostBasis: 50.0, PurchaseDate: now.AddDate(-1, 0, 0)},  // middle age, low cost
		{Shares: 20, CostBasis: 100.0, PurchaseDate: now.AddDate(-2, 0, 0)}, // oldest, high cost
		{Shares: 15, CostBasis: 75.0, PurchaseDate: now.AddDate(0, -6, 0)},  // newest, mid cost
	}
}

func TestFIFO(t *testing.T) {
	lots := makeLots()
	sorted := FIFO(lots)
	// Oldest first: lot[1], lot[0], lot[2]
	if sorted[0].CostBasis != 100.0 {
		t.Errorf("FIFO[0].CostBasis = %v, want 100 (oldest)", sorted[0].CostBasis)
	}
	if sorted[2].CostBasis != 75.0 {
		t.Errorf("FIFO[2].CostBasis = %v, want 75 (newest)", sorted[2].CostBasis)
	}
}

func TestLIFO(t *testing.T) {
	lots := makeLots()
	sorted := LIFO(lots)
	// Newest first: lot[2], lot[0], lot[1]
	if sorted[0].CostBasis != 75.0 {
		t.Errorf("LIFO[0].CostBasis = %v, want 75 (newest)", sorted[0].CostBasis)
	}
	if sorted[2].CostBasis != 100.0 {
		t.Errorf("LIFO[2].CostBasis = %v, want 100 (oldest)", sorted[2].CostBasis)
	}
}

func TestHighestCostFirst(t *testing.T) {
	lots := makeLots()
	sorted := HighestCostFirst(lots)
	// Highest cost first: lot[1]=100, lot[2]=75, lot[0]=50
	if sorted[0].CostBasis != 100.0 {
		t.Errorf("HighestCostFirst[0].CostBasis = %v, want 100", sorted[0].CostBasis)
	}
	if sorted[1].CostBasis != 75.0 {
		t.Errorf("HighestCostFirst[1].CostBasis = %v, want 75", sorted[1].CostBasis)
	}
	if sorted[2].CostBasis != 50.0 {
		t.Errorf("HighestCostFirst[2].CostBasis = %v, want 50", sorted[2].CostBasis)
	}
}

func TestLotSelectorDoesNotMutateOriginal(t *testing.T) {
	lots := makeLots()
	originalFirst := lots[0].CostBasis
	_ = HighestCostFirst(lots)
	if lots[0].CostBasis != originalFirst {
		t.Errorf("LotSelector mutated original slice")
	}
}

func TestUnrealizedGain(t *testing.T) {
	lot := TaxLot{Shares: 100, CostBasis: 50.0}
	// Price up: gain
	gain := UnrealizedGain(lot, 75.0)
	if gain != 2500.0 {
		t.Errorf("UnrealizedGain(price=75) = %v, want 2500", gain)
	}
	// Price down: loss
	loss := UnrealizedGain(lot, 40.0)
	if loss != -1000.0 {
		t.Errorf("UnrealizedGain(price=40) = %v, want -1000", loss)
	}
}

func TestIsLongTerm(t *testing.T) {
	now := time.Now()
	longTermLot := TaxLot{PurchaseDate: now.AddDate(-2, 0, 0)}
	shortTermLot := TaxLot{PurchaseDate: now.AddDate(0, -6, 0)}

	if !IsLongTerm(longTermLot, now) {
		t.Errorf("IsLongTerm(2 years ago) = false, want true")
	}
	if IsLongTerm(shortTermLot, now) {
		t.Errorf("IsLongTerm(6 months ago) = true, want false")
	}
}

func TestTaxCostLongTermGain(t *testing.T) {
	now := time.Now()
	lot := TaxLot{Shares: 100, CostBasis: 50.0, PurchaseDate: now.AddDate(-2, 0, 0)}
	rates := TaxRates{ShortTerm: 0.35, LongTerm: 0.15}
	// Gain: 100*(100-50) = 5000, long-term tax: 5000*0.15 = 750
	tax := TaxCost(lot, 100.0, now, rates)
	if tax != 750.0 {
		t.Errorf("TaxCost(long-term gain) = %v, want 750", tax)
	}
}

func TestTaxCostShortTermGain(t *testing.T) {
	now := time.Now()
	lot := TaxLot{Shares: 100, CostBasis: 50.0, PurchaseDate: now.AddDate(0, -6, 0)}
	rates := TaxRates{ShortTerm: 0.35, LongTerm: 0.15}
	// Gain: 5000, short-term tax: 5000*0.35 = 1750
	tax := TaxCost(lot, 100.0, now, rates)
	if tax != 1750.0 {
		t.Errorf("TaxCost(short-term gain) = %v, want 1750", tax)
	}
}

func TestTaxCostLoss(t *testing.T) {
	now := time.Now()
	lot := TaxLot{Shares: 100, CostBasis: 50.0, PurchaseDate: now.AddDate(-2, 0, 0)}
	rates := TaxRates{ShortTerm: 0.35, LongTerm: 0.15}
	// Loss: 100*(30-50) = -2000, tax benefit: -2000*0.15 = -300
	tax := TaxCost(lot, 30.0, now, rates)
	if tax != -300.0 {
		t.Errorf("TaxCost(loss) = %v, want -300 (tax benefit)", tax)
	}
}

func TestRebalanceGeneratesTrades(t *testing.T) {
	now := time.Now()
	holdings := []Holding{
		{
			Ticker:       "VTI",
			TargetWeight: 0.6,
			Lots:         []TaxLot{{Shares: 100, CostBasis: 50.0, PurchaseDate: now.AddDate(-2, 0, 0)}},
		},
		{
			Ticker:       "BND",
			TargetWeight: 0.4,
			Lots:         []TaxLot{{Shares: 200, CostBasis: 40.0, PurchaseDate: now.AddDate(-2, 0, 0)}},
		},
	}
	prices := map[string]float64{"VTI": 75.0, "BND": 50.0}
	// VTI: 7500 (42.86%), BND: 10000 (57.14%), Total: 17500
	// Target: VTI: 10500 (60%), BND: 7000 (40%)
	// VTI needs +3000, BND needs -3000

	config := RebalanceConfig{
		TaxRates:    DefaultTaxRates(),
		LotSelector: FIFO,
		AsOf:        now,
	}
	trades := Rebalance(holdings, prices, config)

	if len(trades) != 2 {
		t.Fatalf("Rebalance() returned %d trades, want 2", len(trades))
	}

	// Find VTI trade (buy)
	var vtiBuy, bndSell *Trade
	for i := range trades {
		if trades[i].Ticker == "VTI" {
			vtiBuy = &trades[i]
		} else if trades[i].Ticker == "BND" {
			bndSell = &trades[i]
		}
	}

	if vtiBuy == nil || vtiBuy.Amount < 2999 || vtiBuy.Amount > 3001 {
		t.Errorf("VTI buy amount = %v, want ~3000", vtiBuy.Amount)
	}
	if bndSell == nil || bndSell.Amount > -2999 || bndSell.Amount < -3001 {
		t.Errorf("BND sell amount = %v, want ~-3000", bndSell.Amount)
	}
}

func TestRebalanceTaxCostVariesByLotSelector(t *testing.T) {
	now := time.Now()
	// Create holding with multiple lots at different cost bases
	holdings := []Holding{
		{
			Ticker:       "VTI",
			TargetWeight: 0.4, // Overweight, will sell
			Lots: []TaxLot{
				{Shares: 50, CostBasis: 30.0, PurchaseDate: now.AddDate(-2, 0, 0)},  // low cost = high gain
				{Shares: 50, CostBasis: 90.0, PurchaseDate: now.AddDate(-2, 0, 0)},  // high cost = low gain
			},
		},
		{
			Ticker:       "BND",
			TargetWeight: 0.6,
			Lots:         []TaxLot{{Shares: 50, CostBasis: 100.0, PurchaseDate: now.AddDate(-2, 0, 0)}},
		},
	}
	prices := map[string]float64{"VTI": 100.0, "BND": 100.0}
	// VTI: 10000 (66.7%), BND: 5000 (33.3%), Total: 15000
	// Target: VTI: 6000 (40%), BND: 9000 (60%)
	// VTI needs to sell $4000 = 40 shares

	configFIFO := RebalanceConfig{TaxRates: DefaultTaxRates(), LotSelector: FIFO, AsOf: now}
	configHighCost := RebalanceConfig{TaxRates: DefaultTaxRates(), LotSelector: HighestCostFirst, AsOf: now}

	tradesFIFO := Rebalance(holdings, prices, configFIFO)
	tradesHighCost := Rebalance(holdings, prices, configHighCost)

	taxFIFO := TotalTaxCost(tradesFIFO)
	taxHighCost := TotalTaxCost(tradesHighCost)

	// HighestCostFirst should have lower tax cost (sells high basis lots first)
	if taxHighCost >= taxFIFO {
		t.Errorf("HighestCostFirst tax (%v) should be less than FIFO (%v)", taxHighCost, taxFIFO)
	}
}

func TestRebalanceNoTradesWhenBalanced(t *testing.T) {
	now := time.Now()
	holdings := []Holding{
		{Ticker: "VTI", TargetWeight: 0.6, Lots: []TaxLot{{Shares: 60, CostBasis: 100.0}}},
		{Ticker: "BND", TargetWeight: 0.4, Lots: []TaxLot{{Shares: 40, CostBasis: 100.0}}},
	}
	prices := map[string]float64{"VTI": 100.0, "BND": 100.0}

	config := RebalanceConfig{TaxRates: DefaultTaxRates(), LotSelector: FIFO, AsOf: now, MinTradeSize: 1.0}
	trades := Rebalance(holdings, prices, config)

	if len(trades) != 0 {
		t.Errorf("Rebalance() returned %d trades when balanced, want 0", len(trades))
	}
}
