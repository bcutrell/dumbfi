package database

import (
	"context"
	"database/sql"
	_ "embed"
	"log"
	"time"

	_ "modernc.org/sqlite"
)

//go:embed schema.sql
var ddl string

type PortfolioData struct {
	Cash      float64   `json:"cash"`
	Timestamp time.Time `json:"timestamp"`
}

var queries *Queries
var dbConn *sql.DB

func InitDB() (*sql.DB, error) {
	var err error
	dbConn, err = sql.Open("sqlite", "./dumbfi.db")
	if err != nil {
		return nil, err
	}

	ctx := context.Background()
	if _, err := dbConn.ExecContext(ctx, ddl); err != nil {
		return nil, err
	}

	queries = New(dbConn)
	return dbConn, nil
}

func InitializeData(ctx context.Context) {
	_, err := queries.GetLatestPortfolio(ctx)
	if err == sql.ErrNoRows {
		now := time.Now()
		sampleData := []PortfolioData{
			{Cash: 0, Timestamp: now.Add(-48 * time.Hour)},
			{Cash: 100, Timestamp: now.Add(-24 * time.Hour)},
			{Cash: 150, Timestamp: now},
		}

		for _, data := range sampleData {
			params := CreatePortfolioParams(data)
			_, err := queries.CreatePortfolio(ctx, params)
			if err != nil {
				log.Printf("Error inserting sample data: %v", err)
			}
		}
	} else if err != nil {
		log.Printf("Error checking for existing data: %v", err)
	}
}

func GetAllPortfolios(ctx context.Context) ([]PortfolioData, error) {
	entries, err := queries.GetAllPortfolios(ctx)
	if err != nil {
		return nil, err
	}

	var response []PortfolioData
	for _, entry := range entries {
		response = append(response, PortfolioData{
			Cash:      entry.Cash,
			Timestamp: entry.Timestamp,
		})
	}

	return response, nil
}
