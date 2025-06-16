# face_recognition_utils.py
import cv2
import face_recognition
from database import get_face_encodings, log_detection_to_database
from sms_alert import send_sms_alert

def process_image_for_encodings(image_file):
    """Process an image file and extract face encodings."""
    try:
        image = face_recognition.load_image_file(image_file)
        encodings = face_recognition.face_encodings(image)
        return encodings
    except Exception as e:
        print(f"Error processing image {image_file.filename}: {e}")
        return []

def log_detection(name, category, frame, location="Unknown"):
    """Log a detection event and send SMS alert if necessary."""
    try:
        # Convert frame to bytes for database storage
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Log to database
        log_detection_to_database(name, category, frame_bytes, location)
        
        print(f"ALERT: {category} detected - {name} at {location}")

        # Send SMS alert for criminal or suspicious categories
        if category.lower() in ["criminal", "suspicious"]:
            send_sms_alert(name, category, location, frame)
            
        return True
    except Exception as e:
        print(f"Error logging detection: {e}")
        return False

def process_frame(frame, location="Unknown"):
    """Process a frame for face recognition and detection logging."""
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