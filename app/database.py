import sqlite3

conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT,
    username TEXT,
    dark_mode INTEGER DEFAULT 1,
    streaming INTEGER DEFAULT 1,
    temperature REAL DEFAULT 0.7
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    response TEXT
)
""")

conn.commit()