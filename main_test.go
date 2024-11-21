package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"dumbfi/db"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestMain is used for test setup and teardown
func TestMain(m *testing.M) {
	// Setup before any tests
	setup()

	// Run all tests
	code := m.Run()

	// Cleanup after all tests
	teardown()

	// Exit with test results
	os.Exit(code)
}

func setup() {
	// Add any setup code here
}

func teardown() {
	// Add any cleanup code here
}

// Helper function to create a test database
func setupTestDB(t testing.TB) (*db.Queries, func()) {
	// Create a temporary test database
	testDB, err := sql.Open("sqlite", ":memory:")
	require.NoError(t, err)

	// Initialize schema
	_, err = testDB.ExecContext(context.Background(), ddl)
	require.NoError(t, err)

	// Create queries instance
	q := db.New(testDB)

	return q, func() {
		testDB.Close()
	}
}

// Table driven test example
func TestHandleData(t *testing.T) {
	tests := []struct {
		name           string
		initialCash    float64
		expectedStatus int
		expectedCount  int
	}{
		{
			name:           "single entry",
			initialCash:    1000.0,
			expectedStatus: http.StatusOK,
			expectedCount:  1,
		},
		{
			name:           "empty portfolio",
			initialCash:    0.0,
			expectedStatus: http.StatusOK,
			expectedCount:  0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			q, cleanup := setupTestDB(t)
			defer cleanup()

			// Set global variables used by handlers
			queries = q

			ctx := context.Background()

			// Insert test data if needed
			if tt.initialCash > 0 {
				_, err := q.CreatePortfolio(ctx, db.CreatePortfolioParams{
					Cash:      tt.initialCash,
					Timestamp: time.Now(),
				})
				require.NoError(t, err)
			}

			// Create request
			req := httptest.NewRequest("GET", "/api/data", nil)
			w := httptest.NewRecorder()

			// Test
			handleData(w, req)

			// Verify
			assert.Equal(t, tt.expectedStatus, w.Code)

			var response []PortfolioData
			err := json.NewDecoder(w.Body).Decode(&response)
			require.NoError(t, err)
			assert.Equal(t, tt.expectedCount, len(response))

			if tt.expectedCount > 0 {
				assert.Equal(t, tt.initialCash, response[0].Cash)
			}
		})
	}
}

// Example of testing error conditions
func TestErrorConditions(t *testing.T) {
	// Test with invalid database connection
	t.Run("database error", func(t *testing.T) {
		// Create an invalid database connection
		testDB, err := sql.Open("sqlite", ":memory:") // New connection that won't have tables
		require.NoError(t, err)
		defer testDB.Close()

		// Set up queries with invalid DB
		queries = db.New(testDB)

		req := httptest.NewRequest("GET", "/api/data", nil)
		w := httptest.NewRecorder()
		handleData(w, req)

		assert.Equal(t, http.StatusInternalServerError, w.Code)
	})
}

// Test for data validation
func TestDataValidation(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	// Set global variables used by handlers
	queries = q

	ctx := context.Background()

	// Test with various edge cases
	testCases := []struct {
		cash     float64
		isValid  bool
		errorMsg string
	}{
		{cash: -1000, isValid: true, errorMsg: ""}, // SQLite doesn't enforce value constraints
		{cash: 1000000000, isValid: true, errorMsg: ""},
		{cash: 0, isValid: true, errorMsg: ""},
	}

	for _, tc := range testCases {
		t.Run(fmt.Sprintf("cash=%.2f", tc.cash), func(t *testing.T) {
			_, err := q.CreatePortfolio(ctx, db.CreatePortfolioParams{
				Cash:      tc.cash,
				Timestamp: time.Now(),
			})

			if tc.isValid {
				assert.NoError(t, err)
			} else {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tc.errorMsg)
			}
		})
	}
}

// Add a benchmark test
func BenchmarkHandleData(b *testing.B) {
	q, cleanup := setupTestDB(b)
	defer cleanup()

	queries = q
	ctx := context.Background()

	// Insert some test data
	_, err := q.CreatePortfolio(ctx, db.CreatePortfolioParams{
		Cash:      1000.0,
		Timestamp: time.Now(),
	})
	require.NoError(b, err)

	// Run the benchmark
	b.ResetTimer() // Reset timer after setup
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest("GET", "/api/data", nil)
		w := httptest.NewRecorder()
		handleData(w, req)
	}
}
