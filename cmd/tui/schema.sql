-- schema.sql
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cash DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME NOT NULL
);