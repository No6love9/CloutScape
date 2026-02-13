"""
Security utilities - Rate limiting, CAPTCHA, authentication
"""
import os
import requests
from functools import wraps
from flask import session, redirect, url_for, request, current_app


def verify_recaptcha(token):
    """Verify reCAPTCHA v3 token"""
    if not token:
        return False
    
    secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
    if not secret_key:
        # Skip verification if not configured
        return True
    
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': token
            }
        )
        result = response.json()
        
        # Check if verification was successful and score is acceptable
        return result.get('success', False) and result.get('score', 0) >= 0.5
        
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False


def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated', False):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function
