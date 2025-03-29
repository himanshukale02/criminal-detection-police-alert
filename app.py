from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, session
import sqlite3
import face_recognition
import numpy as np
import cv2
import os
import pickle
import requests
import threading
import time
from datetime import datetime
from twilio.rest import Client




app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'  # Required for using sessions

# Hardcoded login credentials
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'admin123'

# Database connection helper
def get_db_connection():
    return sqlite3.connect('record.db')

# Record retrieval function
def get_detection_records():
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

IMGUR_CLIENT_ID = ""

def upload_to_imgur(image_path):
    """Uploads an image to Imgur and returns the direct image URL."""
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    with open(image_path, "rb") as image_file:
        response = requests.post(
            "https://api.imgur.com/3/image",
            headers=headers,
            files={"image": image_file}
        )
    
    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        print("❌ Imgur upload failed:", response.json())
        return None

sms_cooldown = {}
SMS_COOLDOWN_TIME = 20  # 2 minutes

def send_sms_alert(name, category, location, frame):
    """Sends an SMS alert with an image link via Imgur."""
    global sms_cooldown
    current_time = time.time()

    # Cooldown Check
    if name in sms_cooldown and (current_time - sms_cooldown[name]) < SMS_COOLDOWN_TIME:
        print(f"⏳ SMS alert for {name} skipped due to cooldown.")
        return

    try:
        recipient_number = LOCATION_PHONE_MAPPING.get(location, LOCATION_PHONE_MAPPING["Unknown"])
        message = f"🚨 ALERT: {category} detected - {name} at {location}. Immediate action required!"

        # Save frame locally
        image_path = f"{name}_detected.jpg"
        cv2.imwrite(image_path, frame)

        # Upload to Imgur
        image_url = upload_to_imgur(image_path)
        if image_url:
            message += f" View image: {image_url}"

        # Send SMS
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient_number
        )

        # Update cooldown time
        sms_cooldown[name] = current_time

        # Remove local image file after upload
        os.remove(image_path)

        print(f"✅ SMS Alert Sent to {recipient_number}: {message}")

    except Exception as e:
        print(f"❌ Error sending SMS: {e}")


def log_detection(name, category, frame, location="Unknown"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        cursor.execute('''
            INSERT INTO detection_events (person_name, category, last_location, detected_frame)
            VALUES (?, ?, ?, ?)
        ''', (name, category, location, frame_bytes))
        conn.commit()
        conn.close()
        print(f"ALERT: {category} detected - {name} at {location}")

        if category.lower() in ["criminal", "suspicious"]:
            send_sms_alert(name, category, location, frame)  # ✅ FIXED - Passing 'frame'
    except Exception as e:
        print(f"Error logging detection: {e}")

def get_face_encodings():
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

client_frames = {}

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))  # Redirect to home after successful login
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)
    
    return render_template('login.html')

# Home Route
@app.route('/')
def home():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)  # Remove the logged_in key from the session
    return redirect(url_for('login'))  # Redirect to the login page


@app.route('/add_record', methods=['GET','POST'])
def add_record():

    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        age = request.form['age']
        city = request.form['city']
        category = request.form['category']
        details = request.form['details']
        image_files = request.files.getlist('images')  # Handling multiple image files
        
        # Insert person details into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO known_faces (name, age, city, category, details) 
            VALUES (?, ?, ?, ?, ?)
            ''', (name, age, city, category, details))
            person_id = cursor.lastrowid  # Get the ID of the newly inserted person
            
            encoding_added = False
            # Process each image file
            for image_file in image_files:
                try:
                    # Load and process the image file for face encodings
                    image = face_recognition.load_image_file(image_file)
                    encodings = face_recognition.face_encodings(image)
                    
                    for encoding in encodings:
                        cursor.execute('''
                        INSERT INTO face_encodings (person_id, encoding) 
                        VALUES (?, ?)
                        ''', (person_id, pickle.dumps(encoding)))  # Store the encoding as a binary pickle
                        encoding_added = True
                except Exception as e:
                    print(f"Error processing image {image_file.filename}: {e}")
            
            if not encoding_added:
                print("No valid face encodings found for the provided images.")
        except Exception as e:
            print(f"Error adding person details to the database: {e}")
        finally:
            conn.commit()
            conn.close()
        
        return redirect(url_for('home'))  # Redirect to home after adding the record
    
    return render_template('add_record.html')  # Render the form on GET request


@app.route('/live_feed')
def live_feed():
    return render_template('live_feed.html')

@app.route('/detection_logs')
def detection_logs():
    # Fetch detection logs from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT person_name, category, last_location, time, detected_frame 
        FROM detection_events 
        ORDER BY time DESC
    ''')
    logs = cursor.fetchall()
    conn.close()
    
    # Render the logs page
    return render_template('detection_logs.html', logs=logs)


@app.route('/view_records')
def view_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch known faces and their corresponding encodings from the database
    cursor.execute('''
        SELECT kf.id, kf.name, kf.age, kf.city, kf.category, kf.details, fe.encoding
        FROM known_faces kf
        LEFT JOIN face_encodings fe ON kf.id = fe.person_id
    ''')
    
    known_faces_data = cursor.fetchall()
    conn.close()

    # Prepare the data to pass to the template
    known_faces = []
    for data in known_faces_data:
        person_id, name, age, city, category, details, encoding_binary = data
        if encoding_binary:
            encoding = pickle.loads(encoding_binary).tolist()  # Convert to list
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
    
    # Render the page with known faces and their encodings
    return render_template('view_records.html', known_faces=known_faces)

@app.route('/video_feed/<client_id>')
def video_feed(client_id):
    return Response(generate_frame(client_id),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frame(client_id):
    while True:
        if client_id in client_frames:
            frame = client_frames[client_id]
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/upload_frame/<client_id>', methods=['POST'])
def upload_frame(client_id):
    try:
        data = request.files['frame'].read()
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        client_frames[client_id] = frame
        detected_info = process_frame(frame, client_id)
        return jsonify({"status": "frame processed", "detected_info": detected_info})
    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def process_frame(frame, location="Unknown"):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    known_encodings, known_ids, face_dict = get_face_encodings()
    detected_info = []
    
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            person_id = known_ids[first_match_index]
            person_info = face_dict[person_id]
            name = person_info['name']
            category = person_info['category']
            detected_info.append({'name': name, 'category': category})
            log_detection(name, category, frame, location)
    
    return detected_info

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
