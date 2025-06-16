# database.py
import sqlite3
import pickle
from config import DATABASE_NAME

def get_db_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DATABASE_NAME)

def get_detection_records():
    """Retrieve detection records from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT person_name, category, last_location, time 
        FROM detection_events 
        ORDER BY time DESC
    ''')
    records = cursor.fetchall()
    conn.close()
    return records

def get_face_encodings():
    """Retrieve face encodings and associated data from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT person_id, encoding FROM face_encodings")
    rows = cursor.fetchall()
    known_encodings = [pickle.loads(row[1]) for row in rows]
    known_ids = [row[0] for row in rows]
    
    cursor.execute("SELECT id, name, category FROM known_faces")
    face_rows = cursor.fetchall()
    face_dict = {row[0]: {'name': row[1], 'category': row[2]} for row in face_rows}
    conn.close()
    return known_encodings, known_ids, face_dict

def add_person_to_database(name, age, city, category, details, encodings_list):
    """Add a person and their face encodings to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert person details
        cursor.execute('''
        INSERT INTO known_faces (name, age, city, category, details) 
        VALUES (?, ?, ?, ?, ?)
        ''', (name, age, city, category, details))
        person_id = cursor.lastrowid
        
        # Insert face encodings
        for encoding in encodings_list:
            cursor.execute('''
            INSERT INTO face_encodings (person_id, encoding) 
            VALUES (?, ?)
            ''', (person_id, pickle.dumps(encoding)))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding person to database: {e}")
        return False
    finally:
        conn.close()

def log_detection_to_database(name, category, frame_bytes, location="Unknown"):
    """Log a detection event to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detection_events (person_name, category, last_location, detected_frame)
            VALUES (?, ?, ?, ?)
        ''', (name, category, location, frame_bytes))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging detection to database: {e}")
        return False

def get_all_known_faces():
    """Retrieve all known faces and their data from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT kf.id, kf.name, kf.age, kf.city, kf.category, kf.details, fe.encoding
        FROM known_faces kf
        LEFT JOIN face_encodings fe ON kf.id = fe.person_id
    ''')
    
    known_faces_data = cursor.fetchall()
    conn.close()
    
    known_faces = []
    for data in known_faces_data:
        person_id, name, age, city, category, details, encoding_binary = data
        if encoding_binary:
            encoding = pickle.loads(encoding_binary).tolist()
        else:
            encoding = None
        known_faces.append({
            'name': name,
            'age': age,
            'city': city,
            'category': category,
            'details': details,
            'encoding': encoding
        })
    
    return known_faces

def get_detection_logs():
    """Retrieve detection logs from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT person_name, category, last_location, time, detected_frame 
        FROM detection_events 
        ORDER BY time DESC
    ''')
    logs = cursor.fetchall()
    conn.close()
    return logs



def delete_person_by_name_and_category(name, category):
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM known_faces WHERE name = ? AND category = ?", (name, category))
        result = cursor.fetchone()
        
        if result:
            person_id = result[0]
            cursor.execute("DELETE FROM known_faces WHERE id = ?", (person_id,))
            conn.commit()
            conn.close()
            return True
        else:
            print("No matching person found.")
            return False

    except Exception as e:
        print(f"Error deleting person: {e}")
        return False

