"""
Discord Bot for CloutScape Platform
"""
import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import requests
import json
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://web:5000')
PRICE_ALERT_CHANNEL_ID = int(os.getenv('PRICE_ALERT_CHANNEL_ID', '0'))
ORDERS_CHANNEL_ID = int(os.getenv('ORDERS_CHANNEL_ID', '0'))
NOTIFICATION_CHANNEL_ID = int(os.getenv('DISCORD_NOTIFICATION_CHANNEL_ID', '0'))

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    """Bot ready event"""
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
    # Send startup notification
    if NOTIFICATION_CHANNEL_ID:
        channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
        if channel:
            await channel.send("🚀 **CloutScape Discord Bot is online!**")
    
    # Start background tasks
    check_price_changes.start()
    update_member_count.start()


@bot.tree.command(name="price", description="Show current OSRS GP rate")
async def price_command(interaction: discord.Interaction):
    """Show current GP rate"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/prices/live")
        data = response.json()
        
        our_price = data.get('our_price', 0)
        savings = data.get('savings_percent', 0)
        
        embed = discord.Embed(
            title="💰 Current OSRS GP Rates",
            description=f"**Our Price:** ${our_price:.2f} per 1M GP\n**You Save:** {savings:.1f}% vs competitors",
            color=discord.Color.gold()
        )
        
        # Add competitor prices
        competitors = data.get('competitor_prices', {})
        if competitors:
            comp_text = "\n".join([f"**{name}:** ${price:.2f}" for name, price in competitors.items()])
            embed.add_field(name="Competitor Prices", value=comp_text, inline=False)
        
        embed.set_footer(text="CloutScape - Your Degenerate Gambling Paradise")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"Error fetching prices: {e}", ephemeral=True)


@bot.tree.command(name="reward", description="Claim your purchase rewards")
async def reward_command(interaction: discord.Interaction):
    """Claim rewards"""
    user = interaction.user
    # Placeholder for actual verification logic
    reward_code = f"CLOUT-{os.urandom(4).hex().upper()}"
    
    await interaction.response.send_message(
        f"Thank you for your purchase, {user.display_name}! 🎁\n\n"
        f"Your reward code is: `{reward_code}`\n"
        "Please use it in-game or on our platform.",
        ephemeral=True
    )
    
    # Notify admin channel
    if NOTIFICATION_CHANNEL_ID:
        channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
        if channel:
            await channel.send(f"🚀 **New Reward Claimed**\nUser: {user.mention} ({user.id})\nCode: `{reward_code}`")


@bot.tree.command(name="leaderboard", description="Display top 10 clout points")
async def leaderboard_command(interaction: discord.Interaction):
    """Display leaderboard"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/leaderboard?limit=10")
        data = response.json()
        
        embed = discord.Embed(
            title="🏆 Clout Points Leaderboard",
            description="Top 10 degenerates by clout points",
            color=discord.Color.blue()
        )
        
        for entry in data:
            embed.add_field(
                name=f"#{entry['rank']} {entry['username']}",
                value=f"{entry['clout_points']:,} points",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"Error fetching leaderboard: {e}", ephemeral=True)


async def send_discord_notification(message: str):
    """Utility function to send notifications to designated channel"""
    await bot.wait_until_ready()
    if NOTIFICATION_CHANNEL_ID:
        channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
        if channel:
            await channel.send(message)


@tasks.loop(minutes=15)
async def check_price_changes():
    """Check for price changes and send alerts"""
    if PRICE_ALERT_CHANNEL_ID == 0:
        return
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/prices/live")
        data = response.json()
        our_price = data.get('our_price', 0)
        
        # In a real app, compare with previous price stored in DB
        pass
            
    except Exception as e:
        logger.error(f"Error checking price changes: {e}")


@tasks.loop(hours=1)
async def update_member_count():
    """Update member count in API"""
    try:
        for guild in bot.guilds:
            member_count = guild.member_count
            # TODO: Send to API
            logger.info(f"Guild {guild.name} has {member_count} members")
    except Exception as e:
        logger.error(f"Error updating member count: {e}")


def run_bot():
    """Run the Discord bot"""
    if not DISCORD_BOT_TOKEN:
        logger.warning("DISCORD_BOT_TOKEN not set, skipping bot")
        return
    
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    run_bot()
