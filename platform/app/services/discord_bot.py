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

# Bot configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://web:5000')
PRICE_ALERT_CHANNEL_ID = int(os.getenv('PRICE_ALERT_CHANNEL_ID', '0'))
ORDERS_CHANNEL_ID = int(os.getenv('ORDERS_CHANNEL_ID', '0'))

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    """Bot ready event"""
    print(f'{bot.user} has connected to Discord!')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
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


@bot.tree.command(name="stake", description="Log a gambling result")
@app_commands.describe(
    amount="Amount won or lost (in GP)",
    result="Did you win or lose?",
    game="Type of game"
)
@app_commands.choices(result=[
    app_commands.Choice(name="Win", value="win"),
    app_commands.Choice(name="Loss", value="loss")
])
@app_commands.choices(game=[
    app_commands.Choice(name="Duel Arena", value="duel"),
    app_commands.Choice(name="Staking", value="staking"),
    app_commands.Choice(name="Flower Poker", value="flower")
])
async def stake_command(
    interaction: discord.Interaction,
    amount: int,
    result: app_commands.Choice[str],
    game: app_commands.Choice[str]
):
    """Log gambling result"""
    await interaction.response.send_message(
        f"Gambling log submitted! **{result.name}** of {amount:,} GP in {game.name}. "
        f"Awaiting admin approval for clout points.",
        ephemeral=True
    )
    
    # TODO: Send to API to create gambling log


@bot.tree.command(name="referral", description="Get your referral link")
async def referral_command(interaction: discord.Interaction):
    """Get referral link"""
    # TODO: Fetch user's referral code from API
    await interaction.response.send_message(
        "Your referral link: https://cloutscape.org/ref/YOUR_CODE\n"
        "Share it to earn rewards!",
        ephemeral=True
    )


@tasks.loop(minutes=15)
async def check_price_changes():
    """Check for price changes and send alerts"""
    if PRICE_ALERT_CHANNEL_ID == 0:
        return
    
    try:
        # Get current price
        response = requests.get(f"{API_BASE_URL}/api/v1/prices/live")
        data = response.json()
        
        our_price = data.get('our_price', 0)
        
        # Check if price changed significantly (>2%)
        # TODO: Store previous price and compare
        
        channel = bot.get_channel(PRICE_ALERT_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="📊 Price Update",
                description=f"New price: **${our_price:.2f}** per 1M GP",
                color=discord.Color.green()
            )
            # await channel.send(embed=embed)
            
    except Exception as e:
        print(f"Error checking price changes: {e}")


@tasks.loop(hours=1)
async def update_member_count():
    """Update member count in API"""
    try:
        for guild in bot.guilds:
            member_count = guild.member_count
            # TODO: Send to API
            print(f"Guild {guild.name} has {member_count} members")
    except Exception as e:
        print(f"Error updating member count: {e}")


def run_bot():
    """Run the Discord bot"""
    if not DISCORD_BOT_TOKEN:
        print("DISCORD_BOT_TOKEN not set, skipping bot")
        return
    
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    run_bot()
