"""
Discord Webhook Helper
"""
import os
import requests
import json

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')


def send_discord_webhook(title, description, color=0xFFD700, fields=None):
    """Send a Discord webhook message"""
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL not set, skipping webhook")
        return False
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": None
    }
    
    if fields:
        embed["fields"] = fields
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending webhook: {e}")
        return False


def notify_new_order(order):
    """Send notification for new order"""
    fields = [
        {"name": "Order ID", "value": order.id, "inline": True},
        {"name": "Amount", "value": f"{order.amount_gp:,} GP", "inline": True},
        {"name": "Price", "value": f"${order.price_usd:.2f}", "inline": True},
        {"name": "RSN", "value": order.in_game_rsn or "N/A", "inline": True}
    ]
    
    send_discord_webhook(
        title="🛒 New Order Placed",
        description="A new gold order has been placed!",
        color=0x00FF00,
        fields=fields
    )


def notify_price_change(old_price, new_price, change_percent):
    """Send notification for significant price change"""
    if abs(change_percent) < 2:
        return  # Only notify for >2% changes
    
    direction = "📈" if change_percent > 0 else "📉"
    
    send_discord_webhook(
        title=f"{direction} Price Change Alert",
        description=f"Price changed from ${old_price:.2f} to ${new_price:.2f} ({change_percent:+.1f}%)",
        color=0xFF0000 if change_percent > 0 else 0x00FF00
    )
