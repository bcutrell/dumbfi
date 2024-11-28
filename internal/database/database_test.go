// internal/database/database_test.go
package database

import (
	"context"
	"testing"

	"dumbfi/sqlc/models"

	"github.com/google/go-cmp/cmp"
	_ "github.com/mattn/go-sqlite3"
)

func TestQueries(t *testing.T) {
	t.Parallel()

	schemaPath := "../../sqlc/schema/schema.sql"
	db, cleanup, err := NewTestDB(schemaPath)
	if err != nil {
		t.Fatalf("failed to setup test db: %v", err)
	}
	defer cleanup()

	ctx := context.Background()

	// Create account
	account, err := db.CreateAccount(ctx, models.CreateAccountParams{
		Name: "Test Portfolio",
		Cash: 10000.00,
	})
	if err != nil {
		t.Fatal(err)
	}

	// Get account
	fetched, err := db.GetAccount(ctx, account.ID)
	if err != nil {
		t.Fatal(err)
	}

	if diff := cmp.Diff(account, fetched); diff != "" {
		t.Errorf("account mismatch:\n%s", diff)
	}

	// Update Cash
	updated, err := db.UpdateAccountCash(ctx, models.UpdateAccountCashParams{
		ID:   account.ID,
		Cash: 1000.00,
	})
	if err != nil {
		t.Fatal(err)
	}

	expectedCash := 11000.00 // Original 10000 + 1000
	if diff := cmp.Diff(expectedCash, updated.Cash); diff != "" {
		t.Errorf("cash mismatch:\n%s", diff)
	}
}
