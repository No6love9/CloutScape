"""
Price Scheduler - Runs price updates every 15 minutes
"""
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from app import create_app, db
from app.services.price_fetcher import update_prices
from app.services.webhook import notify_price_change

# Create app context
app = create_app()

def scheduled_price_update():
    """Run price update with app context"""
    with app.app_context():
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled price update...")
        
        # Get old price
        from app import redis_client
        old_price_str = redis_client.get('our_price')
        old_price = float(old_price_str) if old_price_str else 0
        
        # Update prices
        result = update_prices()
        
        if result:
            new_price = result.get('our_price', 0)
            
            # Check for significant change
            if old_price > 0:
                change_percent = ((new_price - old_price) / old_price) * 100
                
                if abs(change_percent) >= 2:
                    notify_price_change(old_price, new_price, change_percent)
            
            print(f"Price update completed: ${new_price:.2f}")
        else:
            print("Price update failed")


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    
    # Schedule price updates every 15 minutes
    scheduler.add_job(
        scheduled_price_update,
        'interval',
        minutes=15,
        id='price_update',
        name='Update competitor prices',
        replace_existing=True
    )
    
    print("Price scheduler started. Running every 15 minutes...")
    
    # Run once immediately
    scheduled_price_update()
    
    # Start scheduler
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped")
