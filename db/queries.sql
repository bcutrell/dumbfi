-- queries.sql
-- name: GetAllPortfolios :many
SELECT * FROM portfolios ORDER BY timestamp DESC;

-- name: CreatePortfolio :one
INSERT INTO portfolios (cash, timestamp)
VALUES (?, ?) RETURNING *;

-- name: GetLatestPortfolio :one
SELECT * FROM portfolios 
ORDER BY timestamp DESC 
LIMIT 1;

-- name: DeletePortfolio :exec
DELETE FROM portfolios 
WHERE id = ?;