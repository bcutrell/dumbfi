package bt

import (
	"context"
	"dumbfi/internal/database"
	models "dumbfi/sqlc/models"
	"fmt"
	"time"
)

type Backtest struct {
	ctx          context.Context
	db           *database.DB
	Account      models.Account
	TradeHistory []models.Trade
}

// NewBacktest creates a new backtest with a custom name
func NewBacktest(db *database.DB, initialCash float64, name string) (*Backtest, error) {
	ctx := context.Background()

	// If no name is provided, use the timestamp-based name
	if name == "" {
		name = fmt.Sprintf("Backtest_%s", time.Now().Format("2006-01-02"))
	}

	// Create a new account for this backtest
	account, err := db.CreateAccount(ctx, models.CreateAccountParams{
		Name: name,
		Cash: initialCash,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create account: %w", err)
	}

	return &Backtest{
		ctx:     ctx,
		db:      db,
		Account: account,
	}, nil
}

func NewBacktestWithDefaultDB(initialCash float64, name string) (*Backtest, error) {
	db, err := database.New()
	if err != nil {
		return nil, fmt.Errorf("failed to create database connection: %w", err)
	}

	return NewBacktest(db, initialCash, name)
}

func NewBacktestWithTimestamp(db *database.DB, initialCash float64) (*Backtest, error) {
	return NewBacktest(db, initialCash, "")
}
