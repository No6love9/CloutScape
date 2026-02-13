"""
Authentication routes (Discord OAuth2)
"""
from flask import Blueprint, redirect, url_for, session, request, current_app, jsonify
from app import db
from app.models import User
import requests
import uuid

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    """Redirect to Discord OAuth"""
    discord_client_id = current_app.config['DISCORD_CLIENT_ID']
    redirect_uri = current_app.config['DISCORD_REDIRECT_URI']
    
    oauth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={discord_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=identify%20email"
    )
    
    return redirect(oauth_url)


@auth_bp.route('/callback')
def callback():
    """Discord OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        return redirect(url_for('main.index'))
    
    # Exchange code for access token
    token_url = "https://discord.com/api/oauth2/token"
    data = {
        'client_id': current_app.config['DISCORD_CLIENT_ID'],
        'client_secret': current_app.config['DISCORD_CLIENT_SECRET'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': current_app.config['DISCORD_REDIRECT_URI']
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        token_response = requests.post(token_url, data=data, headers=headers)
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json['access_token']
        
        # Get user info
        user_url = "https://discord.com/api/users/@me"
        user_headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_url, headers=user_headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Check if user exists
        user = User.query.filter_by(discord_id=user_data['id']).first()
        
        if not user:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                discord_id=user_data['id'],
                username=user_data['username'],
                email=user_data.get('email'),
                avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
                referral_code=str(uuid.uuid4())[:8].upper()
            )
            db.session.add(user)
            db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['avatar_url'] = user.avatar_url
        
        return redirect(url_for('main.index'))
        
    except Exception as e:
        current_app.logger.error(f"OAuth error: {e}")
        return redirect(url_for('main.index'))


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('main.index'))


@auth_bp.route('/me')
def me():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.filter_by(id=session['user_id']).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'clout_points': user.clout_points,
        'referral_code': user.referral_code
    }), 200
