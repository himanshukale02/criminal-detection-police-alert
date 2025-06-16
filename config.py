# config.py
import os

# Twilio Configuration
TWILIO_ACCOUNT_SID = 'AC3d227cdc37aecc8ac2d1b0c1d2e5f872'
TWILIO_AUTH_TOKEN = 'c40680e1060c42868d08f72f9ce34ae2'
TWILIO_PHONE_NUMBER = '+16083363703'

# Mapping locations to alert phone numbers
LOCATION_PHONE_MAPPING = {
    "Mall Entrance": "+919421839924",
    "Airport Security": "+919421839924",
    "Railway Station": "+919421839924",
    "Unknown": "+919421839924"  # Default recipient if location is unknown
}

# Flask Configuration
SECRET_KEY = 'your_secret_key'

# Login Credentials
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'admin123'

# Database Configuration
DATABASE_NAME = 'record.db'

# Image Upload Configuration
IMGUR_CLIENT_ID = "2e89354639c6f5d"

# SMS Configuration
SMS_COOLDOWN_TIME = 300  # 5 minutes

#IMGBB
IMGBB_API_KEY = "e1281e086ffdf05f8fa95426969ff811"