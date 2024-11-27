package database

import (
	"database/sql"
	"dumbfi/sqlc/db"
	"fmt"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

type DB struct {
	*sql.DB
	*db.Queries
}

func New() (*DB, error) {
	dbPath := os.Getenv("BLUEPRINT_DB_URL")
	if dbPath == "" {
		dbPath = "local.db"
	}

	sqlDB, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("database connection failed: %w", err)
	}

	if err := sqlDB.Ping(); err != nil {
		return nil, fmt.Errorf("database ping failed: %w", err)
	}

	// Create tables
	if err := createTables(sqlDB); err != nil {
		return nil, fmt.Errorf("table creation failed: %w", err)
	}

	queries := db.New(sqlDB)

	return &DB{
		DB:      sqlDB,
		Queries: queries,
	}, nil
}

func createTables(db *sql.DB) error {
	schema, err := os.ReadFile("sqlc/schema/schema.sql")
	if err != nil {
		return fmt.Errorf("failed to read schema: %w", err)
	}

	_, err = db.Exec(string(schema))
	return err
}
