package bt

import (
	"context"
	"dumbfi/internal/database"  // DB wrapper
	models "dumbfi/sqlc/models" // sqlc code
	"fmt"
	"time"
)

type Backtest struct {
	ctx          context.Context
	db           *database.DB
	Account      models.Account
	TradeHistory []models.Trade
}

func NewBacktest(db *database.DB, initialCash float64) (*Backtest, error) {
	ctx := context.Background()
	// db, err := database.New()
	// if err != nil {
	// 	return nil, fmt.Errorf("failed to create database connection: %w", err)
	// }

	// Create a new account for this backtest
	account, err := db.CreateAccount(ctx, models.CreateAccountParams{
		Name: fmt.Sprintf("Backtest_%s", time.Now().Format("2006-01-02")),
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
