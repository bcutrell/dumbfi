package main

import (
	"embed"
	"encoding/json"
	"html/template"
	"log"
	"net/http"
	"time"
)

//go:embed ui/*
var content embed.FS

type PortfolioData struct {
	Cash      float64   `json:"cash"`
	Timestamp time.Time `json:"timestamp"`
}

var data []PortfolioData

func main() {
	// Initialize with some sample data
	data = []PortfolioData{
		{Cash: 0, Timestamp: time.Now().Add(-48 * time.Hour)},
		{Cash: 100, Timestamp: time.Now().Add(-24 * time.Hour)},
		{Cash: 150, Timestamp: time.Now()},
	}

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
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}
