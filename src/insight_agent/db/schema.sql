CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    content TEXT NOT NULL,
    published_date TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    sentiment TEXT   
);