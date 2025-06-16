import cv2
import requests
import time
import uuid

# Unique client ID
CLIENT_ID = "Airport Security"  
# SERVER_URL = f"http://34.47.217.32:8080/upload_frame/{CLIENT_ID}"
SERVER_URL = f"http://192.168.177.239:5000/upload_frame/{CLIENT_ID}"

def send_frame(frame):
    try: 
        
        _, encoded_frame = cv2.imencode('.jpg', frame)

        
        files = {'frame': ('frame.jpg', encoded_frame.tobytes(), 'image/jpeg')}

        
        response = requests.post(SERVER_URL, files=files,timeout=15)
        if response.status_code == 200:
            print("Frame sent successfully:", response.json())
        else:
            print("Error sending frame:", response.status_code, response.text)
    except Exception as e:
        print("Exception occurred while sending frame:", e)

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    try:
        print(f"Client ID: {CLIENT_ID}")
        print("Press 'q' to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read from webcam.")
                break

            
            cv2.imshow('Client Live Feed', frame)

            
            send_frame(frame)

           
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.2)  
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()