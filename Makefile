DB_FILE ?= local.db

.PHONY: init sqlc run

init: ## Initialize dev environment
	@sqlite3 $(DB_FILE) < sqlc/schema/schema.sql
	@make sqlc

sqlc: ## Generate SQLC code
	@sqlc generate -f sqlc/sqlc.yaml

run: ## Run the application
	@go run cmd/api/main.go

test:
	@go test -v ./...