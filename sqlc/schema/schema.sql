CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    balance DECIMAL(20,2) NOT NULL,  -- available cash balance
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Holdings represent current positions aggregated by symbol
CREATE TABLE IF NOT EXISTS holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL,       -- total shares/contracts held
    avg_price DECIMAL(10,2) NOT NULL,-- average cost basis
    market_value DECIMAL(20,2),      -- current market value
    unrealized_pnl DECIMAL(20,2),    -- unrealized profit/loss
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE(account_id, symbol)
);

-- Tax lots track individual purchase lots for tax purposes
CREATE TABLE IF NOT EXISTS lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    holding_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL,              -- original quantity in this lot
    remaining_quantity INTEGER NOT NULL,    -- quantity still held
    cost_basis DECIMAL(10,2) NOT NULL,      -- price paid per share
    purchase_date DATETIME NOT NULL,
    status TEXT NOT NULL,                   -- 'open', 'partial', 'closed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (holding_id) REFERENCES holdings(id)
);

-- Trades track all transactions
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    lot_id INTEGER,                  -- NULL for sells
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,              -- 'buy' or 'sell'
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    trade_date DATETIME NOT NULL,
    strategy TEXT NOT NULL,
    commission DECIMAL(10,2) DEFAULT 0.0,
    realized_pnl DECIMAL(20,2),      -- NULL for buys
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (lot_id) REFERENCES lots(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_holdings_account ON holdings(account_id);
CREATE INDEX IF NOT EXISTS idx_lots_account ON lots(account_id);
CREATE INDEX IF NOT EXISTS idx_lots_holding ON lots(holding_id);
CREATE INDEX IF NOT EXISTS idx_trades_account ON trades(account_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_lot ON trades(lot_id);