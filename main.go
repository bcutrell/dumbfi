package main

import (
	"context"
	"database/sql"
	"embed"
	"encoding/json"
	"html/template"
	"log"
	"net/http"
	"time"

	"dumbfi/db"

	_ "modernc.org/sqlite"
)

//go:embed ui/*
var content embed.FS

type PortfolioData struct {
	Cash      float64   `json:"cash"`
	Timestamp time.Time `json:"timestamp"`
}

// Global variables
var (
	queries *db.Queries
	dbConn  *sql.DB
)

//go:embed db/schema.sql
var ddl string

func main() {
	ctx := context.Background()

	// Initialize SQLite database
	var err error
	dbConn, err = sql.Open("sqlite", "./dumbfi.db")
	if err != nil {
		log.Fatal("Error opening database:", err)
	}
	defer dbConn.Close()

	// create tables
	if _, err := dbConn.ExecContext(ctx, ddl); err != nil {
		log.Fatal("Error creating tables:", err)
	}

	// Create queries instance
	queries = db.New(dbConn)

	// Initialize with some sample data if the database is empty
	initializeData(ctx)

	// Serve static files
	http.Handle("/static/", http.FileServer(http.FS(content)))

	// API endpoints
	http.HandleFunc("/api/data", handleData)

	// Home Page
	http.HandleFunc("/", handleHomePage)

	log.Println("Server starting on http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func initializeData(ctx context.Context) {
	// Check if we have any entries
	_, err := queries.GetLatestPortfolio(ctx)
	if err == sql.ErrNoRows {
		// Add sample data
		now := time.Now()
		sampleData := []PortfolioData{
			{Cash: 0, Timestamp: now.Add(-48 * time.Hour)},
			{Cash: 100, Timestamp: now.Add(-24 * time.Hour)},
			{Cash: 150, Timestamp: now},
		}

		for _, data := range sampleData {
			_, err := queries.CreatePortfolio(ctx, db.CreatePortfolioParams{
				Cash:      data.Cash,
				Timestamp: data.Timestamp,
			})
			if err != nil {
				log.Printf("Error inserting sample data: %v", err)
			}
		}
	} else if err != nil {
		log.Printf("Error checking for existing data: %v", err)
	}
}

func handleHomePage(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFS(content, "ui/index.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = tmpl.Execute(w, nil)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func handleData(w http.ResponseWriter, r *http.Request) {
	ctx := context.Background()

	entries, err := queries.GetAllPortfolios(ctx)
	if err != nil {
		http.Error(w, "Error fetching data", http.StatusInternalServerError)
		return
	}

	// Convert to PortfolioData format
	var response []PortfolioData
	for _, entry := range entries {
		response = append(response, PortfolioData{
			Cash:      entry.Cash,
			Timestamp: entry.Timestamp,
		})
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
