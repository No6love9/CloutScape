"""
Admin dashboard routes
"""
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, current_app
from app import db, redis_client
from app.models import Order, User, GamblingLog, PriceSnapshot
from app.utils.security import admin_required
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def check_admin_auth():
    """Check if admin is authenticated"""
    return session.get('admin_authenticated', False)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD']):
            session['admin_authenticated'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid credentials')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard overview"""
    # Get statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_users = User.query.count()
    pending_gambling_logs = GamblingLog.query.filter_by(approved=False).count()
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Get current prices from Redis
    current_prices = redis_client.get('current_prices')
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         total_users=total_users,
                         pending_gambling_logs=pending_gambling_logs,
                         recent_orders=recent_orders,
                         current_prices=current_prices)


@admin_bp.route('/orders')
@admin_required
def orders():
    """Order management page"""
    status_filter = request.args.get('status', 'all')
    
    query = Order.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@admin_bp.route('/orders/<order_id>/update', methods=['POST'])
@admin_required
def update_order(order_id):
    """Update order status"""
    order = Order.query.filter_by(id=order_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status in ['pending', 'paid', 'processing', 'completed', 'refunded']:
        order.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': new_status}), 200
    
    return jsonify({'error': 'Invalid status'}), 400


@admin_bp.route('/users')
@admin_required
def users():
    """User management page"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/gambling-logs')
@admin_required
def gambling_logs():
    """Gambling logs approval page"""
    logs = GamblingLog.query.order_by(GamblingLog.created_at.desc()).all()
    return render_template('admin/gambling_logs.html', logs=logs)


@admin_bp.route('/gambling-logs/<log_id>/approve', methods=['POST'])
@admin_required
def approve_gambling_log(log_id):
    """Approve a gambling log"""
    log = GamblingLog.query.filter_by(id=log_id).first()
    
    if not log:
        return jsonify({'error': 'Log not found'}), 404
    
    log.approved = True
    
    # Award clout points
    user = User.query.filter_by(id=log.user_id).first()
    if user:
        points = (log.amount_won - log.amount_lost) // 1_000_000  # 1 point per 1M GP
        user.clout_points += points
    
    db.session.commit()
    
    return jsonify({'success': True}), 200


@admin_bp.route('/prices')
@admin_required
def prices():
    """Price monitoring and override page"""
    # Get current prices from Redis
    current_prices = redis_client.get('current_prices')
    
    # Get recent price history
    recent_snapshots = PriceSnapshot.query.order_by(PriceSnapshot.created_at.desc()).limit(50).all()
    
    return render_template('admin/prices.html', 
                         current_prices=current_prices,
                         recent_snapshots=recent_snapshots)


@admin_bp.route('/prices/override', methods=['POST'])
@admin_required
def override_price():
    """Manually override our price"""
    data = request.get_json()
    new_price = data.get('price')
    
    if not new_price or float(new_price) <= 0:
        return jsonify({'error': 'Invalid price'}), 400
    
    # Set override in Redis
    redis_client.set('price_override', new_price, ex=3600)  # Expire after 1 hour
    
    return jsonify({'success': True, 'price': new_price}), 200


@admin_bp.route('/logs')
@admin_required
def logs():
    """Log viewer page"""
    return render_template('admin/logs.html')
