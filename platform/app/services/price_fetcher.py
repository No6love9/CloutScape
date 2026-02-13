"""
Price Intelligence Engine - Scraping and price calculation
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from app import db, redis_client
from app.models import PriceSnapshot
import numpy as np


# Competitor configurations
COMPETITORS = {
    'PlayerAuctions': {
        'url': 'https://www.playerauctions.com/osrs-gold/',
        'selector': '.price-value',
        'enabled': True
    },
    'Sythe': {
        'url': 'https://www.sythe.org/forums/old-school-runescape-gold/',
        'selector': '.price',
        'enabled': False  # Requires login
    },
    'OSRS Exchange': {
        'url': 'https://osrs.exchange/',
        'selector': '.gold-price',
        'enabled': True
    },
    'Eldorado': {
        'url': 'https://www.eldorado.gg/old-school-runescape/gold',
        'selector': '.price-amount',
        'enabled': True
    },
    'RPGStash': {
        'url': 'https://www.rpgstash.com/runescape-2007-gold.html',
        'selector': '.product-price',
        'enabled': True
    }
}

# Price algorithm settings
COST_FLOOR = 0.20  # Minimum price per 1M GP (USD)
PROFIT_MARGIN = 0.05  # 5% minimum profit margin
DISCOUNT_RATE = 0.85  # 15% below median


async def scrape_competitor_price(competitor_name, config):
    """Scrape price from a single competitor"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            await page.goto(config['url'], timeout=30000)
            await page.wait_for_timeout(2000)  # Wait for dynamic content
            
            # Try to extract price
            price_element = await page.query_selector(config['selector'])
            if price_element:
                price_text = await price_element.inner_text()
                # Parse price (remove $ and convert to float)
                price = float(price_text.replace('$', '').replace(',', '').strip())
                
                await browser.close()
                return price
            
            await browser.close()
            return None
            
    except Exception as e:
        print(f"Error scraping {competitor_name}: {e}")
        return None


async def fetch_all_competitor_prices():
    """Fetch prices from all enabled competitors"""
    tasks = []
    competitor_names = []
    
    for name, config in COMPETITORS.items():
        if config['enabled']:
            tasks.append(scrape_competitor_price(name, config))
            competitor_names.append(name)
    
    prices = await asyncio.gather(*tasks)
    
    # Combine results
    results = {}
    for name, price in zip(competitor_names, prices):
        if price is not None:
            results[name] = price
    
    return results


def calculate_our_price(competitor_prices):
    """Calculate our price based on competitor prices"""
    if not competitor_prices:
        # Use cached price or default
        cached = redis_client.get('our_price')
        return float(cached) if cached else COST_FLOOR * (1 + PROFIT_MARGIN)
    
    prices = list(competitor_prices.values())
    
    # Remove outliers using IQR method
    if len(prices) >= 4:
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
    else:
        filtered_prices = prices
    
    # Calculate median
    median_price = np.median(filtered_prices)
    
    # Apply discount
    our_price = median_price * DISCOUNT_RATE
    
    # Enforce cost floor
    min_price = COST_FLOOR * (1 + PROFIT_MARGIN)
    our_price = max(our_price, min_price)
    
    return round(our_price, 2)


def update_prices():
    """Main function to update all prices (called by scheduler)"""
    try:
        # Check for manual override
        override = redis_client.get('price_override')
        if override:
            our_price = float(override)
            competitor_prices = json.loads(redis_client.get('competitor_prices') or '{}')
        else:
            # Fetch competitor prices
            competitor_prices = asyncio.run(fetch_all_competitor_prices())
            
            # Calculate our price
            our_price = calculate_our_price(competitor_prices)
        
        # Store in Redis (expire after 1 hour)
        redis_client.setex('competitor_prices', 3600, json.dumps(competitor_prices))
        redis_client.setex('our_price', 3600, str(our_price))
        
        # Calculate average and savings
        if competitor_prices:
            avg_competitor = np.mean(list(competitor_prices.values()))
            savings_percent = ((avg_competitor - our_price) / avg_competitor) * 100
        else:
            avg_competitor = 0
            savings_percent = 0
        
        current_prices = {
            'our_price': our_price,
            'competitor_prices': competitor_prices,
            'average_competitor': round(avg_competitor, 2),
            'savings_percent': round(savings_percent, 2),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        redis_client.setex('current_prices', 3600, json.dumps(current_prices))
        
        # Save to database for history
        for competitor, price in competitor_prices.items():
            snapshot = PriceSnapshot(
                competitor=competitor,
                price_per_m=price,
                our_price_per_m=our_price
            )
            db.session.add(snapshot)
        
        db.session.commit()
        
        print(f"Prices updated: Our price ${our_price}, Avg competitor ${avg_competitor}")
        
        return current_prices
        
    except Exception as e:
        print(f"Error updating prices: {e}")
        return None


def get_current_prices():
    """Get current prices from Redis cache"""
    cached = redis_client.get('current_prices')
    if cached:
        return json.loads(cached)
    
    # If cache is empty, trigger update
    return update_prices() or {
        'our_price': COST_FLOOR * (1 + PROFIT_MARGIN),
        'competitor_prices': {},
        'average_competitor': 0,
        'savings_percent': 0,
        'updated_at': datetime.utcnow().isoformat()
    }


def get_price_history(days=7):
    """Get historical price data"""
    since = datetime.utcnow() - timedelta(days=days)
    snapshots = PriceSnapshot.query.filter(
        PriceSnapshot.created_at >= since
    ).order_by(PriceSnapshot.created_at.asc()).all()
    
    # Group by timestamp
    history = {}
    for snapshot in snapshots:
        timestamp = snapshot.created_at.isoformat()
        if timestamp not in history:
            history[timestamp] = {
                'our_price': float(snapshot.our_price_per_m),
                'competitors': {}
            }
        history[timestamp]['competitors'][snapshot.competitor] = float(snapshot.price_per_m)
    
    return history
