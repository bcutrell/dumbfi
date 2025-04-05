package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/mux"
)

type MarketData struct {
	Date   time.Time          `json:"date"`
	Prices map[string]float64 `json:"prices"`
}

type Portfolio struct {
	UserID      string             `json:"user_id"`
	Cash        float64            `json:"cash"`
	Holdings    map[string]float64 `json:"holdings"`
	TargetAlloc map[string]float64 `json:"target_allocation"`
}

type GameState struct {
	CurrentDate time.Time `json:"current_date"`
	StartDate   time.Time `json:"start_date"`
	EndDate     time.Time `json:"end_date"`
	Speed       int       `json:"speed"`
}

var (
	marketData = make(map[string]MarketData)
	portfolios = make(map[string]Portfolio)
	gameState  = GameState{
		StartDate:   time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
		EndDate:     time.Date(2024, 12, 31, 0, 0, 0, 0, time.UTC),
		CurrentDate: time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
		Speed:       1,
	}
)

func getMarketData(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	date := params["date"]

	data, exists := marketData[date]
	if !exists {
		http.Error(w, "Data not found for date", http.StatusNotFound)
		return
	}

	json.NewEncoder(w).Encode(data)
}

func getPortfolio(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	userID := params["user_id"]

	portfolio, exists := portfolios[userID]
	if !exists {
		// New user, initialize portfolio
		portfolio = Portfolio{
			UserID:      userID,
			Cash:        100000, // Starting with $100k
			Holdings:    make(map[string]float64),
			TargetAlloc: make(map[string]float64),
		}
		portfolios[userID] = portfolio
	}

	json.NewEncoder(w).Encode(portfolio)
}

func executeRebalance(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	userID := params["user_id"]

	portfolio, exists := portfolios[userID]
	if !exists {
		http.Error(w, "Portfolio not found", http.StatusNotFound)
		return
	}

	// Get current prices
	dateStr := gameState.CurrentDate.Format("2006-01-02")
	prices, exists := marketData[dateStr]
	if !exists {
		http.Error(w, "Market data not available for current date", http.StatusNotFound)
		return
	}

	// Calculate total portfolio value
	totalValue := portfolio.Cash
	for ticker, shares := range portfolio.Holdings {
		if price, ok := prices.Prices[ticker]; ok {
			totalValue += shares * price
		}
	}

	// Would perform rebalance logic here

	json.NewEncoder(w).Encode(portfolio)
}

func advanceTime(w http.ResponseWriter, r *http.Request) {
	var request struct {
		Days int `json:"days"`
	}

	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// Prevent advancing past end date
	newDate := gameState.CurrentDate.AddDate(0, 0, request.Days)
	if newDate.After(gameState.EndDate) {
		newDate = gameState.EndDate
	}

	gameState.CurrentDate = newDate
	json.NewEncoder(w).Encode(gameState)
}

func setupRoutes() *mux.Router {
	router := mux.NewRouter()

	router.HandleFunc("/api/market/{date}", getMarketData).Methods("GET")
	router.HandleFunc("/api/portfolio/{user_id}", getPortfolio).Methods("GET")
	router.HandleFunc("/api/portfolio/{user_id}/rebalance", executeRebalance).Methods("POST")
	router.HandleFunc("/api/game/advance", advanceTime).Methods("POST")

	return router
}

func main() {
	// TODO load historical market data
	router := setupRoutes()
	// TODO middleware for logging, CORS, etc.

	server := &http.Server{
		Handler:      router,
		Addr:         ":8080",
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Println("Server starting on port 8080")
	log.Fatal(server.ListenAndServe())
}
