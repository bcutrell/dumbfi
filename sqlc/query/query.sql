-- name: CreateAccount :one
INSERT INTO accounts (
    name,
    cash
) VALUES (?, ?) RETURNING *;

-- name: GetAccount :one
SELECT * FROM accounts WHERE id = ?;

-- name: ListAccounts :many
SELECT * FROM accounts ORDER BY id;

-- name: UpdateAccountCash :one
UPDATE accounts 
SET cash = cash + ?,
    updated_at = CURRENT_TIMESTAMP
WHERE id = ? 
RETURNING *;

-- name: DeleteAccount :exec
DELETE FROM accounts WHERE id = ?;

-- name: UpsertHolding :one
INSERT INTO holdings (
    account_id,
    symbol,
    quantity,
    avg_price,
    market_value,
    unrealized_pnl
) VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT (account_id, symbol) DO UPDATE
SET quantity = quantity + excluded.quantity,
    avg_price = ((avg_price * quantity) + (excluded.quantity * excluded.avg_price)) 
               / (quantity + excluded.quantity),
    market_value = excluded.market_value,
    unrealized_pnl = excluded.unrealized_pnl,
    updated_at = CURRENT_TIMESTAMP
RETURNING *;

-- name: GetHolding :one
SELECT * FROM holdings WHERE id = ?;

-- name: GetHoldingBySymbol :one
SELECT * FROM holdings 
WHERE account_id = ? AND symbol = ?;

-- name: ListAccountHoldings :many
SELECT h.*, a.name as account_name, a.cash as account_cash
FROM holdings h
JOIN accounts a ON h.account_id = a.id
WHERE h.account_id = ?
ORDER BY h.market_value DESC;

-- name: UpdateHolding :one
UPDATE holdings
SET quantity = ?,
    avg_price = ?,
    market_value = ?,
    unrealized_pnl = ?,
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?
RETURNING *;

-- name: UpdateHoldingMarketValue :one
UPDATE holdings
SET market_value = ?,
    unrealized_pnl = market_value - (avg_price * quantity),
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?
RETURNING *;

-- name: DeleteHolding :exec
DELETE FROM holdings WHERE id = ?;

-- name: CreateLot :one
INSERT INTO tax_lots (
    account_id,
    holding_id,
    symbol,
    quantity,
    remaining_quantity,
    cost_basis,
    purchase_date,
    status
) VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING *;

-- name: GetLot :one
SELECT * FROM tax_lots WHERE id = ?;

-- name: ListAccountTaxLots :many
SELECT l.*, h.avg_price as holding_avg_price, h.market_value as holding_market_value
FROM tax_lots l
JOIN holdings h ON l.holding_id = h.id
WHERE l.account_id = ?
ORDER BY l.purchase_date;

-- name: ListHoldingTaxLots :many
SELECT * FROM tax_lots 
WHERE holding_id = ? 
ORDER BY purchase_date;

-- name: UpdateTaxLotstatus :one
UPDATE tax_lots
SET status = ?,
    remaining_quantity = ?
WHERE id = ?
RETURNING *;

-- name: DeleteTaxLot :exec
DELETE FROM tax_lots WHERE id = ?;

-- name: CreateTrade :one
INSERT INTO trades (
    account_id,
    tax_lot_id,
    symbol,
    side,
    quantity,
    price,
    trade_date,
    strategy,
    commission,
    realized_pnl,
    notes
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING *;

-- name: GetTrade :one
SELECT * FROM trades WHERE id = ?;

-- name: ListAccountTrades :many
SELECT t.*, l.cost_basis as tax_lot_cost_basis, l.purchase_date as tax_lot_purchase_date
FROM trades t
LEFT JOIN tax_lots l ON t.lot_id = l.id
WHERE t.account_id = ?
ORDER BY t.trade_date DESC;

-- name: ListSymbolTrades :many
SELECT * FROM trades 
WHERE account_id = ? AND symbol = ?
ORDER BY trade_date DESC;

-- name: GetTradesByDateRange :many
SELECT * FROM trades
WHERE account_id = ?
  AND trade_date BETWEEN ? AND ?
ORDER BY trade_date;

-- name: DeleteTrade :exec
DELETE FROM trades WHERE id = ?;

-- name: GetTaxLotsByFIFO :many
SELECT * FROM tax_lots
WHERE account_id = ?
  AND symbol = ?
  AND remaining_quantity > 0
  AND status IN ('open', 'partial')
ORDER BY purchase_date ASC;

-- name: GetTaxLotsByLIFO :many
SELECT * FROM tax_lots
WHERE account_id = ?
  AND symbol = ?
  AND remaining_quantity > 0
  AND status IN ('open', 'partial')
ORDER BY purchase_date DESC;

-- name: GetAccountPerformance :one
SELECT 
    a.id,
    a.name,
    a.cash,
    COALESCE(SUM(h.market_value), 0) as total_market_value,
    COALESCE(SUM(h.unrealized_pnl), 0) as total_unrealized_pnl,
    COALESCE((SELECT SUM(realized_pnl) FROM trades WHERE account_id = a.id), 0) as total_realized_pnl
FROM accounts a
LEFT JOIN holdings h ON h.account_id = a.id
WHERE a.id = ?
GROUP BY a.id, a.name, a.cash;

-- name: GetSymbolPerformance :one
SELECT 
    symbol,
    SUM(CASE WHEN side = 'buy' THEN quantity ELSE -quantity END) as net_quantity,
    AVG(CASE WHEN side = 'buy' THEN price ELSE NULL END) as avg_buy_price,
    AVG(CASE WHEN side = 'sell' THEN price ELSE NULL END) as avg_sell_price,
    SUM(COALESCE(realized_pnl, 0)) as total_realized_pnl,
    COUNT(CASE WHEN side = 'buy' THEN 1 END) as buy_trades,
    COUNT(CASE WHEN side = 'sell' THEN 1 END) as sell_trades
FROM trades
WHERE account_id = ? AND symbol = ?
GROUP BY symbol;