// dumbbt/backtest.go
package dumbbt

import (
	"context"
	"dumbfi/internal/database"
	"time"
)

type Trade struct {
	EntryDate  time.Time
	ExitDate   time.Time
	EntryPrice float64
	ExitPrice  float64
	Size       float64
	Side       string
	Symbol     string
}

type Result struct {
	Trades        []Trade
	TotalReturn   float64
	WinRate       float64
	MaxDrawdown   float64
	SharpeRatio   float64
	StartingValue float64
	EndingValue   float64
}

type DataProvider interface {
	GetPriceData(ctx context.Context, symbol string, startTime, endTime time.Time) ([]PriceData, error)
}

type PriceData struct {
	Timestamp time.Time
	Open      float64
	High      float64
	Low       float64
	Close     float64
	Volume    float64
}

type Strategy interface {
	GenerateSignals(ctx context.Context, data []PriceData) ([]Trade, error)
}

type DatabaseDataProvider struct {
	DB *database.Queries
}

func NewDatabaseDataProvider(db *database.Queries) *DatabaseDataProvider {
	return &DatabaseDataProvider{DB: db}
}

func (d *DatabaseDataProvider) GetPriceData(ctx context.Context, symbol string, startTime, endTime time.Time) ([]PriceData, error) {
	return nil, nil
}
