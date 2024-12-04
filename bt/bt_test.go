package bt

import (
	"dumbfi/internal/database"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockStrategy implements Strategy interface for testing
type MockStrategy struct {
	mock.Mock
}

func TestBacktest(t *testing.T) {
	schemaPath := "../sqlc/schema/schema.sql"
	db, cleanup, err := database.NewTestDB(schemaPath)
	if err != nil {
		t.Fatalf("failed to setup test db: %v", err)
	}
	defer cleanup()

	t.Run("NewBacktest with custom name", func(t *testing.T) {
		backtest, err := NewBacktest(db, 1000000.0, "MyCustomBacktest")
		assert.Nil(t, err)
		assert.NotNil(t, backtest)
		assert.Equal(t, 1000000.0, backtest.Account.Cash)
		assert.Equal(t, "MyCustomBacktest", backtest.Account.Name)
	})

	t.Run("NewBacktest with timestamp", func(t *testing.T) {
		backtest, err := NewBacktest(db, 1000000.0, "")
		assert.Nil(t, err)
		assert.NotNil(t, backtest)
		assert.Equal(t, 1000000.0, backtest.Account.Cash)
		expectedPrefix := "Backtest_" + time.Now().Format("2006-01-02")
		assert.Contains(t, backtest.Account.Name, expectedPrefix)
	})

	t.Run("NewBacktestWithTimestamp for backwards compatibility", func(t *testing.T) {
		backtest, err := NewBacktestWithTimestamp(db, 1000000.0)
		assert.Nil(t, err)
		assert.NotNil(t, backtest)
		assert.Equal(t, 1000000.0, backtest.Account.Cash)
		expectedPrefix := "Backtest_" + time.Now().Format("2006-01-02")
		assert.Contains(t, backtest.Account.Name, expectedPrefix)
	})
}
