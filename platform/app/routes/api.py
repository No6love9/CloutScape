"""
API endpoints for CloutScape Platform
"""
from flask import Blueprint, jsonify, request, session, abort
from app import db, limiter
from app.models import Order, User, GamblingLog
from app.services.price_fetcher import get_current_prices, get_price_history
from app.utils.security import verify_recaptcha, login_required
from app.services.telegram_bot import send_notification as send_telegram_notification
from app.services.discord_bot import send_discord_notification
import uuid
import os
import hmac
import hashlib
import asyncio

api_bp = Blueprint('api', __name__)

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

def verify_github_signature(payload_body, signature_header):
    """Verify GitHub webhook signature"""
    if not GITHUB_WEBHOOK_SECRET:
        return True  # Skip verification if secret not set (not recommended for production)
    
    if not signature_header:
        return False
        
    hash_object = hmac.new(GITHUB_WEBHOOK_SECRET.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


@api_bp.route('/prices/live', methods=['GET'])
@limiter.limit("60 per minute")
def get_live_prices():
    """Get current live prices from all competitors"""
    prices = get_current_prices()
    return jsonify(prices), 200


@api_bp.route('/prices/history', methods=['GET'])
@limiter.limit("30 per minute")
def get_prices_history():
    """Get historical price data"""
    days = request.args.get('days', default=7, type=int)
    if days > 30:
        days = 30
    
    history = get_price_history(days=days)
    return jsonify(history), 200


@api_bp.route('/leaderboard', methods=['GET'])
@limiter.limit("60 per minute")
def get_leaderboard():
    """Get top users by clout points"""
    limit = request.args.get('limit', default=10, type=int)
    if limit > 100:
        limit = 100
    
    top_users = User.query.order_by(User.clout_points.desc()).limit(limit).all()
    
    leaderboard = [
        {
            'rank': idx + 1,
            'username': user.username,
            'clout_points': user.clout_points,
            'avatar_url': user.avatar_url
        }
        for idx, user in enumerate(top_users)
    ]
    
    return jsonify(leaderboard), 200


@api_bp.route('/orders', methods=['POST'])
@limiter.limit("10 per minute")
@login_required
def create_order():
    """Create a new gold order (authenticated users only)"""
    data = request.get_json()
    
    if not data or 'amount_gp' not in data or 'in_game_rsn' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    recaptcha_token = data.get('recaptcha_token')
    if not verify_recaptcha(recaptcha_token):
        return jsonify({'error': 'reCAPTCHA verification failed'}), 400
    
    prices = get_current_prices()
    our_price = prices.get('our_price', 0)
    
    amount_gp = int(data['amount_gp'])
    total_usd = (amount_gp / 1_000_000) * our_price
    
    order = Order(
        id=str(uuid.uuid4()),
        user_id=session.get('user_id'),
        amount_gp=amount_gp,
        price_usd=total_usd,
        in_game_rsn=data['in_game_rsn'],
        status='pending'
    )
    
    db.session.add(order)
    db.session.commit()
    
    # Notify via Discord and Telegram
    message = f"🛒 **New Order Created**\nOrder ID: `{order.id}`\nAmount: {amount_gp:,} GP\nTotal: ${total_usd:.2f}\nRSN: `{order.in_game_rsn}`"
    asyncio.run(send_discord_notification(message))
    asyncio.run(send_telegram_notification(message))
    
    return jsonify({
        'order_id': order.id,
        'amount_gp': order.amount_gp,
        'price_usd': float(order.price_usd),
        'status': order.status
    }), 201


@api_bp.route('/webhooks/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhooks and notify Telegram/Discord"""
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_github_signature(request.data, signature):
        abort(403)

    event = request.headers.get('X-GitHub-Event')
    payload = request.json
    message = ""

    if event == 'push':
        repo_name = payload['repository']['full_name']
        pusher = payload['pusher']['name']
        for commit in payload['commits']:
            message += f"🚀 **[{repo_name}]** New commit by {pusher}: {commit['message']}\n"
    elif event == 'pull_request':
        action = payload['action']
        pr_title = payload['pull_request']['title']
        sender = payload['sender']['login']
        message = f"📢 **[PR]** {sender} {action} PR: '{pr_title}'"
    elif event == 'issues':
        action = payload['action']
        issue_title = payload['issue']['title']
        sender = payload['sender']['login']
        message = f"🐛 **[Issue]** {sender} {action} issue: '{issue_title}'"

    if message:
        asyncio.run(send_discord_notification(message))
        asyncio.run(send_telegram_notification(message))

    return jsonify({'status': 'success'}), 200
