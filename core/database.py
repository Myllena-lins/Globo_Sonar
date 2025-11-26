import sqlite3
from pathlib import Path

DB_PATH = Path("mxf.db")

def create_tables():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        path TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

create_tables()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
