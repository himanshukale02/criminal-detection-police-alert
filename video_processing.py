# video_processing.py
import cv2
import numpy as np
from face_recognition_utils import process_frame

# Global dictionary to store client frames
client_frames = {}

def store_client_frame(client_id, frame):
    """Store frame for a specific client."""
    client_frames[client_id] = frame

def get_client_frame(client_id):
    """Get frame for a specific client."""
    return client_frames.get(client_id)

def generate_frame(client_id):
    """Generate frame stream for video feed."""
    while True:
        if client_id in client_frames:
            frame = client_frames[client_id]
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

def process_uploaded_frame(frame_data, client_id):
    """Process uploaded frame data."""
    try:
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        store_client_frame(client_id, frame)
        detected_info = process_frame(frame, client_id)
        
        return {
            "status": "frame processed", 
            "detected_info": detected_info
        }
    except Exception as e:
        print(f"Error processing frame: {e}")
        return {
            "status": "error", 
            "message": str(e)
        }