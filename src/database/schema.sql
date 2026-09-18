-- Arcana Chess Data Cloud - SQLite Database Schema
-- Optimized for high-throughput batch ingestion and lightning-fast search queries

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twic_issue INTEGER NOT NULL,
    event TEXT,
    site TEXT,
    date TEXT,
    round TEXT,
    white TEXT NOT NULL,
    black TEXT NOT NULL,
    result TEXT NOT NULL,
    white_elo INTEGER,
    black_elo INTEGER,
    eco TEXT,
    pgn TEXT NOT NULL
);

-- Fast lookup indexes for player queries, openings, timelines, and issues
CREATE INDEX IF NOT EXISTS idx_white ON games(white);
CREATE INDEX IF NOT EXISTS idx_black ON games(black);
CREATE INDEX IF NOT EXISTS idx_eco ON games(eco);
CREATE INDEX IF NOT EXISTS idx_date ON games(date);
CREATE INDEX IF NOT EXISTS idx_twic ON games(twic_issue);

-- Metadata store for engine version, sync timestamps, and total games
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Tracking table for incremental TWIC issue synchronizations
CREATE TABLE IF NOT EXISTS processed_issues (
    issue INTEGER PRIMARY KEY,
    processed_at TEXT NOT NULL,
    games_count INTEGER NOT NULL
);
