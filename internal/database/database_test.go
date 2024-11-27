// internal/database/database_test.go
package database

import (
	"context"
	"database/sql"
	"os"
	"testing"

	"dumbfi/sqlc/db"

	"github.com/google/go-cmp/cmp"
	_ "github.com/mattn/go-sqlite3"
)

func setupTestDB(t *testing.T) (*db.Queries, func()) {
	// Create temp database
	sqlDB, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatalf("failed to open test db: %v", err)
	}

	// Read schema
	schema, err := os.ReadFile("../../sqlc/schema/schema.sql")
	if err != nil {
		t.Fatalf("failed to read schema: %v", err)
	}

	// Create tables
	if _, err := sqlDB.Exec(string(schema)); err != nil {
		t.Fatalf("failed to create schema: %v", err)
	}

	// Create queries instance
	queries := db.New(sqlDB)

	// Return cleanup function
	cleanup := func() {
		sqlDB.Close()
	}

	return queries, cleanup
}

func TestQueries(t *testing.T) {
	t.Parallel()

	queries, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	// Create account
	account, err := queries.CreateAccount(ctx, db.CreateAccountParams{
		Name:    "Test Portfolio",
		Balance: 10000.00,
	})
	if err != nil {
		t.Fatal(err)
	}

	// Get account
	fetched, err := queries.GetAccount(ctx, account.ID)
	if err != nil {
		t.Fatal(err)
	}

	if diff := cmp.Diff(account, fetched); diff != "" {
		t.Errorf("account mismatch:\n%s", diff)
	}

	// Update balance
	updated, err := queries.UpdateAccountBalance(ctx, db.UpdateAccountBalanceParams{
		ID:      account.ID,
		Balance: 1000.00,
	})
	if err != nil {
		t.Fatal(err)
	}

	expectedBalance := 11000.00 // Original 10000 + 1000
	if diff := cmp.Diff(expectedBalance, updated.Balance); diff != "" {
		t.Errorf("balance mismatch:\n%s", diff)
	}
}
