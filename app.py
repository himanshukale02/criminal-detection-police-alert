# app.py
from flask import Flask
from config import SECRET_KEY
from routes import init_routes

def create_app():
    
    app = Flask(__name__, template_folder='templates')
    app.secret_key = SECRET_KEY
    
    
    init_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)