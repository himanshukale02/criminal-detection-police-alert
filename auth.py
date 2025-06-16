# auth.py
from functools import wraps
from flask import session, redirect, url_for
from config import VALID_USERNAME, VALID_PASSWORD

def authenticate_user(username, password):
    """Authenticate user credentials."""
    return username == VALID_USERNAME and password == VALID_PASSWORD

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def is_logged_in():
    """Check if user is logged in."""
    return 'logged_in' in session and session['logged_in']