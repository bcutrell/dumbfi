package bt

import (
	"dumbfi/internal/database"
	"testing"

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

	t.Run("NewBacktest", func(t *testing.T) {
		backtest, error := NewBacktest(db, 1000000.0)
		assert.Nil(t, error)
		assert.NotNil(t, backtest)
		assert.Equal(t, 1000000.0, backtest.Account.Cash)
	})
}
