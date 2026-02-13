"""
API endpoints for CloutScape Platform
"""
from flask import Blueprint, jsonify, request, session
from app import db, limiter
from app.models import Order, User, GamblingLog
from app.services.price_fetcher import get_current_prices, get_price_history
from app.utils.security import verify_recaptcha, login_required
import uuid

api_bp = Blueprint('api', __name__)


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
    
    # Validate input
    if not data or 'amount_gp' not in data or 'in_game_rsn' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify reCAPTCHA
    recaptcha_token = data.get('recaptcha_token')
    if not verify_recaptcha(recaptcha_token):
        return jsonify({'error': 'reCAPTCHA verification failed'}), 400
    
    # Get current price
    prices = get_current_prices()
    our_price = prices.get('our_price', 0)
    
    # Calculate total
    amount_gp = int(data['amount_gp'])
    total_usd = (amount_gp / 1_000_000) * our_price
    
    # Create order
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
    
    # TODO: Send Discord webhook notification
    
    return jsonify({
        'order_id': order.id,
        'amount_gp': order.amount_gp,
        'price_usd': float(order.price_usd),
        'status': order.status
    }), 201


@api_bp.route('/orders/<order_id>', methods=['GET'])
@limiter.limit("30 per minute")
def get_order_status(order_id):
    """Check order status"""
    order = Order.query.filter_by(id=order_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({
        'order_id': order.id,
        'amount_gp': order.amount_gp,
        'price_usd': float(order.price_usd),
        'status': order.status,
        'created_at': order.created_at.isoformat(),
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
    }), 200


@api_bp.route('/webhook/discord', methods=['POST'])
def discord_webhook():
    """Internal webhook for Discord bot notifications"""
    # TODO: Verify webhook signature
    data = request.get_json()
    
    # Process webhook data
    # This is for internal communication between Discord bot and web app
    
    return jsonify({'status': 'received'}), 200
