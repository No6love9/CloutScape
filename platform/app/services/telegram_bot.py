"""
Telegram Bot for CloutScape Platform (Optional)
"""
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://web:5000')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "Welcome to CloutScape! 🎰\n\n"
        "Use /price to check current GP rates.\n"
        "Visit https://cloutscape.org for more!"
    )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/prices/live")
        data = response.json()
        
        our_price = data.get('our_price', 0)
        savings = data.get('savings_percent', 0)
        
        message = (
            f"💰 **Current OSRS GP Rates**\n\n"
            f"Our Price: ${our_price:.2f} per 1M GP\n"
            f"You Save: {savings:.1f}% vs competitors\n\n"
            f"Buy now at https://cloutscape.org"
        )
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"Error fetching prices: {e}")


def run_telegram_bot():
    """Run the Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set, skipping Telegram bot")
        return
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("price", price_command))
    
    # Run bot
    print("Starting Telegram bot...")
    app.run_polling()


if __name__ == '__main__':
    run_telegram_bot()
