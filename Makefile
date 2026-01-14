# DumbFi Makefile - Cross-language build commands

# Python commands
py-test:
	cd python && uv run pytest

py-test-cov:
	cd python && uv run pytest --cov=dumbfi --cov-report=html --cov-report=term

py-lint:
	cd python && uv run ruff check .

py-format:
	cd python && uv run ruff format .

py-game:
	cd python && uv run python -m games.pyxel_trading

py-notebook:
	cd python && uv run marimo run notebooks/modern_portfolio_theory.py

# Go commands
go-build:
	cd go && go build ./...

go-test:
	cd go && go test ./...

go-backtest:
	cd go && go run cmd/backtest/main.go

go-optimizer:
	cd go && go run cmd/optimizer/main.go

# TypeScript (inkfolio) commands
ts-build:
	cd inkfolio && npm run build

ts-demo:
	cd inkfolio && npm run build && node dist/cli.js

ts-install:
	cd inkfolio && npm install

# Data commands
download-prices:
	cd python && uv run python scripts/download_prices.py

generate-risk-model:
	cd python && uv run python scripts/generate_risk_model.py

# Clean
clean:
	rm -rf python/.venv python/.ruff_cache inkfolio/node_modules go/bin

.PHONY: py-test py-test-cov py-lint py-format py-game py-notebook \
        go-build go-test go-backtest go-optimizer \
        ts-build ts-demo ts-install \
        download-prices generate-risk-model clean
