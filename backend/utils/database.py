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
            urgency INTEGER NOT NULL,
            sender_email TEXT
        )        
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

def addHistoryEntry(content, analysis, sender_email=None):
    conn = getDBConnection()
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
    conn.commit()
    conn.close()

def getHistory(limit = 10):
    conn = getDBConnection()
    recs = conn.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    conn.close()

    return [dict(rec) for rec in recs]

def deleteHistoryEntry(entryId):
    conn = getDBConnection()
    conn.execute('DELETE FROM history WHERE id = ?', (entryId,))
    conn.commit()
    conn.close()

def patchHistoryEntry(entryId, updates):
    conn = getDBConnection()
    fields = []
    values = []
    for key, value in updates.items():
        if key in ['classification', 'urgency']:
            fields.append(f"{key} = ?")
            values.append(value)

        if not fields:
            conn.close()
            return False
    
    query = f"UPDATE history SET {', '.join(fields)} WHERE id = ?"
    values.append(entryId)
    conn.execute(query, tuple(values))
    conn.commit()
    conn.close()
    return True