package server

import (
	"context"
	"log"
	"time"

	"dumbfi/internal/database"
)

func main() {
	// Create database connection
	db, err := database.New()
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Perform health check
	health, err := db.HealthCheck(ctx)
	if err != nil {
		log.Printf("Health check failed: %v", err)
	}

	log.Printf("Database health: %+v", health)
}
