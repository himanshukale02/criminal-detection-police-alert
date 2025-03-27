import cv2
import requests
import time
import uuid

# Unique client ID
CLIENT_ID = "client1"  
SERVER_URL = f"http://192.168.0.139:5000/upload_frame/{CLIENT_ID}"

def send_frame(frame):
    try: 
        # Encode the frame as JPEG
        _, encoded_frame = cv2.imencode('.jpg', frame)

        # Create a dictionary for the frame data
        files = {'frame': ('frame.jpg', encoded_frame.tobytes(), 'image/jpeg')}

        # Send the frame to the server
        response = requests.post(SERVER_URL, files=files)
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

            # Display the frame locally (optional)
            cv2.imshow('Client Live Feed', frame)

            # Send the frame to the server
            send_frame(frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)  # Adjust the frame rate
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()