CREATE TABLE IF NOT EXISTS health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL,
    message TEXT,
    open_connections INTEGER,
    in_use INTEGER,
    idle INTEGER,
    wait_count INTEGER,
    wait_duration TEXT,
    max_idle_closed INTEGER,
    max_lifetime_closed INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);