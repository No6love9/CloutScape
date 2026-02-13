"""
Telegram Bot for CloutScape Platform
"""
import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://web:5000')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! Welcome to CloutScape! 🎰\n\n"
        "Use /price to check current GP rates.\n"
        "Use /reward to claim your purchase rewards.\n"
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


async def reward_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reward command for script purchases"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # Placeholder for actual verification logic
    # In production, you would verify against your database
    reward_code = f"CLOUT-{os.urandom(4).hex().upper()}"
    
    await update.message.reply_text(
        f"Thank you for your purchase, {username}! 🎁\n\n"
        f"Your reward code is: `{reward_code}`\n"
        "Please use it in-game or on our platform.",
        parse_mode='Markdown'
    )
    
    # Notify admin
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🚀 **New Reward Claimed**\nUser: @{username} (ID: {user_id})\nCode: {reward_code}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")


async def send_notification(message: str):
    """Utility function to send notifications to admin chat"""
    if ADMIN_CHAT_ID and TELEGRAM_BOT_TOKEN:
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        async with app:
            await app.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode='Markdown')


def run_telegram_bot():
    """Run the Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping Telegram bot")
        return
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("reward", reward_command))
    
    # Run bot
    logger.info("Starting Telegram bot...")
    app.run_polling()


if __name__ == '__main__':
    run_telegram_bot()
