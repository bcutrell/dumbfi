package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"sync"

	"dumbfi/sqlc/db"

	_ "github.com/mattn/go-sqlite3"
)

type DB struct {
	*sql.DB
	*db.Queries
}

var (
	instance *DB
	once     sync.Once
)

// New creates a new database connection
func New() (*DB, error) {
	var err error
	once.Do(func() {
		dbURL := os.Getenv("BLUEPRINT_DB_URL")
		if dbURL == "" {
			dbURL = "local.db" // Default to local.db if not specified
		}

		var sqlDB *sql.DB
		sqlDB, err = sql.Open("sqlite3", dbURL)
		if err != nil {
			return
		}

		// Test the connection
		if err = sqlDB.Ping(); err != nil {
			return
		}

		instance = &DB{
			DB:      sqlDB,
			Queries: db.New(sqlDB),
		}

		// Ensure tables exist
		if err = instance.createTablesIfNotExist(); err != nil {
			log.Printf("Warning: failed to create tables: %v", err)
		}
	})

	if err != nil {
		return nil, fmt.Errorf("failed to create database connection: %w", err)
	}

	return instance, nil
}

// createTablesIfNotExist ensures all required tables exist
func (db *DB) createTablesIfNotExist() error {
	schema, err := os.ReadFile("sqlc/schema/schema.sql")
	if err != nil {
		return fmt.Errorf("failed to read schema file: %w", err)
	}

	_, err = db.Exec(string(schema))
	if err != nil {
		return fmt.Errorf("failed to create tables: %w", err)
	}

	return nil
}

// Close closes the database connection
func (db *DB) Close() error {
	if db.DB != nil {
		return db.DB.Close()
	}
	return nil
}
