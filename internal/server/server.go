package server

import (
	"encoding/json"
	"log"
	"net/http"

	"dumbfi/internal/database"
)

type Server struct {
	DB *database.DB
}

func New() (*Server, error) {
	db, err := database.New()
	if err != nil {
		return nil, err
	}

	return &Server{DB: db}, nil
}

func (s *Server) Routes() http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("/api/accounts", s.handleAccounts)
	mux.HandleFunc("/", s.handleHome)

	return s.withCORS(mux)
}

func (s *Server) withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func (s *Server) handleAccounts(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	listAccounts, err := s.DB.ListAccounts(ctx)
	if err != nil {
		log.Printf("Error fetching accounts: %v", err)
		http.Error(w, "Error fetching accounts", http.StatusInternalServerError)
		return
	}

	s.writeJSON(w, listAccounts)
}

func (s *Server) handleHome(w http.ResponseWriter, r *http.Request) {
	s.writeJSON(w, map[string]string{"message": "Hello World"})
}

func (s *Server) writeJSON(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(data); err != nil {
		log.Printf("Error writing response: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
}
