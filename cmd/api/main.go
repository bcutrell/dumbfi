package main

import (
	"context"
	"embed"
	"encoding/json"
	"html/template"
	"log"
	"net/http"

	"dumbfi/internal/database"
)

//go:embed ui/*
var content embed.FS

func main() {
	ctx := context.Background()

	// Initialize SQLite database
	dbConn, err := database.InitDB()
	if err != nil {
		log.Fatal("Error initializing database:", err)
	}
	defer dbConn.Close()

	// Initialize with some sample data if the database is empty
	database.InitializeData(ctx)

	// Serve static files
	http.Handle("/static/", http.FileServer(http.FS(content)))

	// API endpoints
	http.HandleFunc("/api/data", handleData)

	// Home Page
	http.HandleFunc("/", handleHomePage)

	log.Println("Server starting on http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
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

	entries, err := database.GetAllPortfolios(ctx)
	if err != nil {
		http.Error(w, "Error fetching data", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entries)
}
