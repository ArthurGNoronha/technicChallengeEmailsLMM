import sqlite3
import json

DATABASE_FILE = 'history.db'

def getDBConnection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initDB():
    conn = getDBConnection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            content TEXT NOT NULL,
            classification TEXT NOT NULL,
            summary TEXT NOT NULL,
            keyPoints TEXT NOT NULL,
            urgency INTEGER NOT NULL
        )        
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

def addHistoryEntry(content, analysis):
    conn = getDBConnection()
    conn.execute(
        'INSERT INTO history (content, classification, summary, keyPoints, urgency) VALUES (?, ?, ?, ?, ?)',
        (
            content,
            analysis.get('type'),
            analysis.get('summary'),
            json.dumps(analysis.get('keyPoints')),
            analysis.get('urgency')
        )
    )
    conn.commit()
    conn.close()

def getHistory(limit = 10):
    conn = getDBConnection()
    recs = conn.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    conn.close()

    return [dict(rec) for rec in recs]