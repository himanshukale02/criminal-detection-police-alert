# sms_alert.py
import time
import cv2
import os
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID, 
    TWILIO_AUTH_TOKEN, 
    TWILIO_PHONE_NUMBER, 
    LOCATION_PHONE_MAPPING, 
    SMS_COOLDOWN_TIME
)
from image_upload import upload_to_imgbb

# Global variable to track SMS cooldown
sms_cooldown = {}

def send_sms_alert(name, category, location, frame):
    """Sends an SMS alert with an image link via Imgur."""
    global sms_cooldown
    current_time = time.time()

    # Cooldown Check
    if name in sms_cooldown and (current_time - sms_cooldown[name]) < SMS_COOLDOWN_TIME:
        print(f"⏳ SMS alert for {name} skipped due to cooldown.")
        return False

    try:
        recipient_number = LOCATION_PHONE_MAPPING.get(location, LOCATION_PHONE_MAPPING["Unknown"])
        message = f"🚨 ALERT: {category} detected - {name} at {location}. Immediate action required!"

        # Save frame locally
        image_path = f"{name}_detected.jpg"
        cv2.imwrite(image_path, frame)

        # Upload to Imgur
        image_url = upload_to_imgbb(image_path)
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
        if os.path.exists(image_path):
            os.remove(image_path)

        print(f"✅ SMS Alert Sent to {recipient_number}: {message}")
        return True

    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        return False