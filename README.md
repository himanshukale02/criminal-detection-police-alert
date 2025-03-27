# 📌 AI-Powered Missing Person and Criminal Identification & Police Alert System

## 🔍 Overview
This cutting-edge platform uses **real-time facial recognition technology** to identify missing persons and criminal suspects from video feeds across multiple locations. When a match is found, the system immediately alerts relevant authorities via SMS, potentially saving crucial time in locating individuals of interest.

## ✨ Key Features

- **Advanced Facial Recognition** - Deep learning algorithms identify individuals by comparing video feed faces against our secure database
- **Multi-Location Monitoring** - Process simultaneous video streams from various locations for comprehensive coverage
- **Instant SMS Notifications** - Location-specific alerts sent to authorities when matches are detected via Twilio API
- **Comprehensive Logging** - Detailed records of all detections including images, timestamps, and location data
- **Secure Admin Dashboard** - Protected interface for system management, record updates, and detection monitoring
- **Centralized Database** - Secure storage for facial encodings, personal information, and all system activities

## 🚀 Technology Stack

| Component | Technology Used |
|-----------|-----------------|
| Backend | Flask (Python) |
| Frontend | HTML/CSS with Jinja Templates |
| Database | SQLite |
| Face Recognition | face_recognition library |
| Video Processing | OpenCV |
| Notifications | Twilio API |

## 🔄 System Workflow

1. **Administrator Authentication**  
   ![Admin Login Interface](https://github.com/user-attachments/assets/095d9220-554d-409d-a4bc-53c9397c2a9d)

2. **Database Management**  
   ![Record Addition Screen](https://github.com/user-attachments/assets/44d164ab-0c13-46e5-b1f9-047668bec2c0)

3. **Video Feed Monitoring**  
   ![Live Monitoring Interface](https://github.com/user-attachments/assets/e8c7761b-26b2-4d79-936b-495ba10cb02e)

4. **Facial Recognition Processing**  
   System continuously analyzes frames for potential matches

5. **Alert Generation**  
   When matches are found:
   - Event is logged in the database
   - SMS alert is dispatched to nearest authorized contact
   - Detection appears on the dashboard

   ![SMS Alert Example](https://github.com/user-attachments/assets/9f42b4e4-389b-4fbd-9e4e-09527a2537ec)

6. **System Management**  
   **Database Records**  
   ![Records Database View](https://github.com/user-attachments/assets/2b94a1f7-5932-4ad8-8dbc-b8f74610493a)  

   **Detection History**  
   ![Log History Screen](https://github.com/user-attachments/assets/aff5a715-1a8d-4b42-aa71-978bf2631b64)

## 🌐 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Dashboard home (authentication required) |
| `/login` | GET/POST | Administrator authentication |
| `/logout` | GET | Session termination |
| `/add_record` | GET/POST | New person/criminal record creation |
| `/view_records` | GET | Database record browsing |
| `/detection_logs` | GET | Historical detection viewing |
| `/live_feed` | GET | Real-time surveillance monitoring |
| `/video_feed/<location>` | GET | Location-specific video streaming |
| `/upload_frame/<location>` | POST | Client device frame submission |

## 🔒 Security Infrastructure

- **Role-Based Access Control** - Session authentication restricts system access to authorized personnel only
- **Anti-Spam Protection** - 5-minute cooldown period prevents notification flooding for the same individual/location
- **Secure Data Storage** - Facial encodings and personal information stored with appropriate security measures

## 🚀 Future Development Roadmap

- **Cloud Migration** - Move to scalable cloud storage for expanded database capabilities
- **Enhanced Recognition Models** - Implement next-generation deep learning for improved accuracy
- **CCTV Integration** - Develop connectors for widespread surveillance system compatibility
- **Real-Time Alert Upgrade** - Implement WebSockets for instantaneous in-app notifications
