import sqlite3
import json
from contextlib import contextmanager

DATABASE_FILE = 'history.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            content TEXT NOT NULL,
            classification TEXT NOT NULL,
            summary TEXT NOT NULL,
            keyPoints TEXT NOT NULL,
            urgency INTEGER NOT NULL,
            sender_email TEXT
        )        
    ''')
    print("Database initialized.")

def add_history_entry(content, analysis, sender_email=None):
    with get_db_connection() as conn:
        conn.execute(
        'INSERT INTO history (content, classification, summary, keyPoints, urgency, sender_email) VALUES (?, ?, ?, ?, ?, ?)',
        (
            content,
            analysis.get('type'),
            analysis.get('summary'),
            json.dumps(analysis.get('keyPoints')),
            analysis.get('urgency'),
            sender_email
        )
    )

def get_history(limit = 10):
    with get_db_connection() as conn:
        recs = conn.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()

    return [dict(rec) for rec in recs]

def delete_history_entry(entry_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM history WHERE id = ?', (entry_id,))

def patch_history_entry(entry_id, updates):
    allowed = {'classification', 'urgency'}
    fields = []
    values = []
    for key, value in updates.items():
        if key in allowed:
            fields.append(f"{key} = ?")
            values.append(value)

    if not fields:
        return False

    query = f"UPDATE history SET {', '.join(fields)} WHERE id = ?"
    values.append(entry_id)

    with get_db_connection() as conn:
        conn.execute(query, tuple(values))
    return True