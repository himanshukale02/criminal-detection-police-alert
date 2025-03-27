import sqlite3

def init_db():
    conn = sqlite3.connect('record.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS known_faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        city TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('criminal', 'missing person', 'suspect', 'other')),
        details TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_encodings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        encoding BLOB NOT NULL,
        FOREIGN KEY (person_id) REFERENCES known_faces(id) ON DELETE CASCADE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detection_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_name TEXT NOT NULL,
        category TEXT NOT NULL,
        last_location TEXT NOT NULL,
        time DATETIME DEFAULT (DATETIME('now', 'localtime')),
        detected_frame BLOB NOT NULL
    )
    ''')

    # Create indexes for faster search
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_person_id ON face_encodings(person_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_person_name ON detection_events(person_name)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
