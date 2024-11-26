-- name: CreateHealthCheck :one
INSERT INTO health_checks (
    status,
    message,
    open_connections,
    in_use,
    idle,
    wait_count,
    wait_duration,
    max_idle_closed,
    max_lifetime_closed
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?
) RETURNING *;

-- name: GetLatestHealthCheck :one
SELECT * FROM health_checks
ORDER BY created_at DESC
LIMIT 1;

-- name: GetHealthChecks :many
SELECT * FROM health_checks
ORDER BY created_at DESC
LIMIT ?;