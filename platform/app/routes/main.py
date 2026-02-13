"""
Main public routes for CloutScape Platform
"""
from flask import Blueprint, render_template, jsonify, request
from app.services.price_fetcher import get_current_prices, get_price_history
from app.utils.helpers import generate_sitemap

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page with hero section and live prices"""
    prices = get_current_prices()
    return render_template('index.html', prices=prices)


@main_bp.route('/prices')
def prices():
    """Dedicated price comparison page"""
    current_prices = get_current_prices()
    history = get_price_history(days=7)
    return render_template('price.html', prices=current_prices, history=history)


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')


@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate dynamic sitemap"""
    xml = generate_sitemap()
    return xml, 200, {'Content-Type': 'application/xml'}


@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'cloutscape-platform'}), 200
