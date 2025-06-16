from flask import render_template, request, redirect, url_for, Response, jsonify, session
from auth import authenticate_user, login_required, is_logged_in
from database import (
    get_detection_records, 
    add_person_to_database, 
    get_all_known_faces, 
    get_detection_logs
)
from face_recognition_utils import process_image_for_encodings
from video_processing import generate_frame, process_uploaded_frame

def init_routes(app):
    
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if authenticate_user(username, password):
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                error = "Invalid username or password"
                return render_template('login.html', error=error)
        
        return render_template('login.html')

    @app.route('/')
    @login_required
    def home():
        return render_template('home.html')

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        session.pop('logged_in', None)
        return redirect(url_for('login'))

    @app.route('/add_record', methods=['GET', 'POST'])
    @login_required
    def add_record():
        if request.method == 'POST':
            
            name = request.form['name']
            age = request.form['age']
            city = request.form['city']
            category = request.form['category']
            details = request.form['details']
            image_files = request.files.getlist('images')
            
            
            all_encodings = []
            for image_file in image_files:
                encodings = process_image_for_encodings(image_file)
                all_encodings.extend(encodings)
            
            
            if all_encodings:
                success = add_person_to_database(name, age, city, category, details, all_encodings)
                if success:
                    print(f"Successfully added {name} to database")
                else:
                    print(f"Failed to add {name} to database")
            else:
                print("No valid face encodings found for the provided images.")
            
            return redirect(url_for('home'))
        
        return render_template('add_record.html')

    @app.route('/live_feed')
    @login_required
    def live_feed():
        return render_template('live_feed.html')

    @app.route('/detection_logs')
    @login_required
    def detection_logs():
        logs = get_detection_logs()
        return render_template('detection_logs.html', logs=logs)

    @app.route('/view_records')
    @login_required
    def view_records():
        known_faces = get_all_known_faces()
        return render_template('view_records.html', known_faces=known_faces)

    @app.route('/video_feed/<client_id>')
    @login_required
    def video_feed(client_id):
        return Response(generate_frame(client_id),
                       mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/upload_frame/<client_id>', methods=['POST'])
    def upload_frame(client_id):  # REMOVED @login_required decorator
        try:
            frame_data = request.files['frame'].read()
            result = process_uploaded_frame(frame_data, client_id)
            
            if result["status"] == "error":
                return jsonify(result), 500
            else:
                return jsonify(result)
                
        except Exception as e:
            print(f"Error in upload_frame route: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/delete_record', methods=['GET', 'POST'])
    def delete_record():
        if request.method == 'POST':
            name = request.form['name']
            category = request.form['category']
            from database import delete_person_by_name_and_category

            success = delete_person_by_name_and_category(name, category)
            if success:
                message = f"Record for {name} ({category}) deleted successfully."
            else:
                message = "Error occurred while deleting the record."
            return render_template('delete_record.html', message=message)
        return render_template('delete_record.html')

