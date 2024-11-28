package database

import (
	"database/sql"
	"dumbfi/sqlc/models"
	"fmt"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

type DB struct {
	*sql.DB
	*models.Queries
}

func New() (*DB, error) {
	dbPath := os.Getenv("DUMBFI_DB_URL")
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

	queries := models.New(sqlDB)

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

func createTablesFromPath(db *sql.DB, path string) error {
	schema, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("failed to read schema: %w", err)
	}

	_, err = db.Exec(string(schema))
	return err
}

func NewTestDB(schemaPath string) (*DB, func(), error) {
	sqlDB, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		return nil, nil, fmt.Errorf("failed to open test db: %w", err)
	}

	// Create tables
	if err := createTablesFromPath(sqlDB, schemaPath); err != nil {
		return nil, nil, fmt.Errorf("table creation failed: %w", err)
	}

	queries := models.New(sqlDB)

	cleanup := func() {
		sqlDB.Close()
	}

	return &DB{
		DB:      sqlDB,
		Queries: queries,
	}, cleanup, nil
}
