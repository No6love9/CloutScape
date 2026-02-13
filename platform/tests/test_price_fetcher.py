"""
Unit tests for price fetcher
"""
import pytest
from app.services.price_fetcher import calculate_our_price, COST_FLOOR, PROFIT_MARGIN


def test_calculate_our_price_with_valid_data():
    """Test price calculation with valid competitor prices"""
    competitor_prices = {
        'Competitor1': 1.00,
        'Competitor2': 0.95,
        'Competitor3': 1.05,
        'Competitor4': 0.98
    }
    
    our_price = calculate_our_price(competitor_prices)
    
    # Should be 15% below median
    assert our_price > 0
    assert our_price < min(competitor_prices.values())


def test_calculate_our_price_respects_floor():
    """Test that price never goes below cost floor"""
    competitor_prices = {
        'Competitor1': 0.10,
        'Competitor2': 0.12
    }
    
    our_price = calculate_our_price(competitor_prices)
    min_price = COST_FLOOR * (1 + PROFIT_MARGIN)
    
    assert our_price >= min_price


def test_calculate_our_price_empty_data():
    """Test price calculation with no competitor data"""
    our_price = calculate_our_price({})
    min_price = COST_FLOOR * (1 + PROFIT_MARGIN)
    
    assert our_price >= min_price


def test_calculate_our_price_outlier_removal():
    """Test that outliers are removed"""
    competitor_prices = {
        'Competitor1': 1.00,
        'Competitor2': 0.95,
        'Competitor3': 1.05,
        'Competitor4': 10.00  # Outlier
    }
    
    our_price = calculate_our_price(competitor_prices)
    
    # Should not be influenced by the outlier
    assert our_price < 1.50
