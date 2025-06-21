CREATE TABLE IF NOT EXISTS session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT,
    ended_at TEXT,
    tags TEXT,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    role TEXT,
    content TEXT,
    tags TEXT,
    timestamp TEXT,
    FOREIGN KEY(session_id) REFERENCES session(id)
);
