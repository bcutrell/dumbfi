package database

import (
	"context"
	"database/sql"
	"fmt"
	"strconv"
)

// HealthCheck performs a health check on the database and returns statistics
func (db *DB) HealthCheck(ctx context.Context) (map[string]string, error) {
	stats := make(map[string]string)

	// Check database connection
	if err := db.PingContext(ctx); err != nil {
		stats["status"] = "down"
		stats["error"] = fmt.Sprintf("db down: %v", err)
		return stats, err
	}

	// Database is up, collect statistics
	stats["status"] = "up"
	stats["message"] = "It's healthy"

	dbStats := db.Stats()

	// Store health check in database
	params := db.CreateHealthCheckParams{
		Status:            stats["status"],
		Message:           sql.NullString{String: stats["message"], Valid: true},
		OpenConnections:   int64(dbStats.OpenConnections),
		InUse:             int64(dbStats.InUse),
		Idle:              int64(dbStats.Idle),
		WaitCount:         dbStats.WaitCount,
		WaitDuration:      dbStats.WaitDuration.String(),
		MaxIdleClosed:     dbStats.MaxIdleClosed,
		MaxLifetimeClosed: dbStats.MaxLifetimeClosed,
	}

	_, err := db.CreateHealthCheck(ctx, params)
	if err != nil {
		return stats, fmt.Errorf("failed to store health check: %w", err)
	}

	// Add statistics to return map
	stats["open_connections"] = strconv.Itoa(dbStats.OpenConnections)
	stats["in_use"] = strconv.Itoa(dbStats.InUse)
	stats["idle"] = strconv.Itoa(dbStats.Idle)
	stats["wait_count"] = strconv.FormatInt(dbStats.WaitCount, 10)
	stats["wait_duration"] = dbStats.WaitDuration.String()
	stats["max_idle_closed"] = strconv.FormatInt(dbStats.MaxIdleClosed, 10)
	stats["max_lifetime_closed"] = strconv.FormatInt(dbStats.MaxLifetimeClosed, 10)

	return stats, nil
}
