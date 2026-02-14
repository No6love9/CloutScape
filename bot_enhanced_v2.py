#!/usr/bin/env python3
import os
os.environ["DISCORD_NO_AUDIO"] = "1"
"""
CloutScape Enhanced Discord Bot v2
Sophisticated RSPS-integrated Discord bot with player authentication and management
"""
import sys
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime
import discord
from discord.ext import commands, tasks
from discord import Permissions
import asyncio
import random
import matplotlib.pyplot as plt
import io

# Import custom modules - assume they exist
try:
    from modules.rsps_integration import RSPSIntegration
    from modules.gambling import GamblingSystem
    from modules.pvp import PvPSystem
    from modules.events import EventSystem
    from modules.rewards import RewardSystem
    from modules.webhooks import WebhookManager
except ImportError as e:
    print(f"Missing module: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================
class Config:
    """Bot configuration"""
    # Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
    GUILD_ID = os.getenv('GUILD_ID')  # Optional: specific guild ID
    # RSPS Configuration
    RSPS_HOST = os.getenv('RSPS_HOST', 'localhost')
    RSPS_PORT = int(os.getenv('RSPS_PORT', 43594))
    CLOUDFLARE_DOMAIN = os.getenv('CLOUDFLARE_DOMAIN', 'play.cloutscape.com')
    # Bot Configuration
    COMMAND_PREFIX = '!'
    BOT_STATUS = 'CloutScape RSPS | !help'
    # Download Links
    CLIENT_DOWNLOAD_URL = os.getenv('CLIENT_DOWNLOAD_URL', 'https://github.com/No6love9/CloutScape/releases/latest/download/client.jar')
    # Enhanced Channel Configuration
    CHANNELS = {
        'announcements': {
            'description': '📢 Server announcements and updates',
            'topic': 'Important announcements for CloutScape RSPS',
            'nsfw': False,
            'category': 'Information',
            'emoji': '📢'
        },
        'giveaways': {
            'description': '🎁 Giveaway announcements and entries',
            'topic': 'Participate in exciting giveaways and win prizes!',
            'nsfw': False,
            'category': 'Events',
            'emoji': '🎁'
        },
        'gambling-logs': {
            'description': '🎰 Real-time gambling activity logs',
            'topic': 'Dice, Poker, Blackjack, Slots, and Roulette results',
            'nsfw': False,
            'category': 'Gaming',
            'emoji': '🎰'
        },
        'pvp-kills': {
            'description': '⚔️ PvP kill logs and loot drops',
            'topic': 'Track PvP activity, kills, and epic loot drops',
            'nsfw': False,
            'category': 'Gaming',
            'emoji': '⚔️'
        },
        'leaderboards': {
            'description': '🏆 Community leaderboards and rankings',
            'topic': 'Top players, achievements, and hall of fame',
            'nsfw': False,
            'category': 'Community',
            'emoji': '🏆'
        },
        'events': {
            'description': '🎯 Event announcements and updates',
            'topic': 'Tournaments, raids, and special events',
            'nsfw': False,
            'category': 'Events',
            'emoji': '🎯'
        },
        'general': {
            'description': '💬 General discussion channel',
            'topic': 'General chat and community discussion',
            'nsfw': False,
            'category': 'Community',
            'emoji': '💬'
        },
        'bot-commands': {
            'description': '🤖 Bot commands and interactions',
            'topic': 'Use bot commands here - Type !help for command list',
            'nsfw': False,
            'category': 'Bot',
            'emoji': '🤖'
        },
        'server-status': {
            'description': '📊 Live server statistics',
            'topic': 'Real-time server status and player count',
            'nsfw': False,
            'category': 'Information',
            'emoji': '📊'
        },
        'game-guide': {
            'description': '🎮 How to play and guides',
            'topic': 'Learn how to play, download client, and get started',
            'nsfw': False,
            'category': 'Information',
            'emoji': '🎮'
        },
        'economy': {
            'description': '💰 Market and trading',
            'topic': 'Buy, sell, and trade items with other players',
            'nsfw': False,
            'category': 'Community',
            'emoji': '💰'
        },
        'support': {
            'description': '🔧 Player support tickets',
            'topic': 'Need help? Create a support ticket here',
            'nsfw': False,
            'category': 'Support',
            'emoji': '🔧'
        },
        'logs': {
            'description': '📝 Bot activity logs',
            'topic': 'System logs and administrative records',
            'nsfw': False,
            'category': 'Admin',
            'emoji': '📝'
        },
        'admin': {
            'description': '👑 Admin-only channel',
            'topic': 'Administrative discussions and server management',
            'nsfw': False,
            'category': 'Admin',
            'emoji': '👑'
        }
    }
    # Enhanced Role Configuration
    ROLES = {
        'Server Owner': {
            'color': discord.Color.from_rgb(220, 20, 60),  # Crimson
            'hoist': True,
            'mentionable': True,
            'permissions': ['administrator'],
            'emoji': '👑'
        },
        'Admin': {
            'color': discord.Color.from_rgb(255, 140, 0),  # Dark Orange
            'hoist': True,
            'mentionable': True,
            'permissions': ['administrator'],
            'emoji': '⚡'
        },
        'Moderator': {
            'color': discord.Color.from_rgb(255, 215, 0),  # Gold
            'hoist': True,
            'mentionable': True,
            'permissions': [
                'manage_messages',
                'kick_members',
                'ban_members',
                'manage_channels'
            ],
            'emoji': '🛡️'
        },
        'Event Manager': {
            'color': discord.Color.from_rgb(218, 165, 32),  # Goldenrod
            'hoist': True,
            'mentionable': True,
            'permissions': [
                'manage_channels',
                'manage_roles',
                'manage_messages'
            ],
            'emoji': '🎯'
        },
        'VIP': {
            'color': discord.Color.from_rgb(138, 43, 226),  # Blue Violet
            'hoist': True,
            'mentionable': True,
            'permissions': [
                'send_messages',
                'embed_links',
                'attach_files',
                'use_external_emojis'
            ],
            'emoji': '💎'
        },
        'Veteran': {
            'color': discord.Color.from_rgb(30, 144, 255),  # Dodger Blue
            'hoist': True,
            'mentionable': False,
            'permissions': [
                'send_messages',
                'embed_links',
                'attach_files'
            ],
            'emoji': '🌟'
        },
        'PvP Legend': {
            'color': discord.Color.from_rgb(139, 0, 0),  # Dark Red
            'hoist': True,
            'mentionable': False,
            'permissions': ['send_messages'],
            'emoji': '⚔️'
        },
        'High Roller': {
            'color': discord.Color.from_rgb(0, 128, 0),  # Green
            'hoist': True,
            'mentionable': False,
            'permissions': ['send_messages'],
            'emoji': '🎰'
        },
        'Member': {
            'color': discord.Color.from_rgb(135, 206, 250),  # Light Sky Blue
            'hoist': False,
            'mentionable': False,
            'permissions': ['send_messages', 'read_message_history'],
            'emoji': '👤'
        },
        'Muted': {
            'color': discord.Color.greyple(),
            'hoist': False,
            'mentionable': False,
            'permissions': ['read_messages'],
            'emoji': '🔇'
        }
    }

# ============================================================================
# Modular RSPS Manager (for wipe, etc.)
# ============================================================================
class RSPSManager:
    def __init__(self):
        self.rsps = RSPSIntegration(Config.RSPS_HOST, Config.RSPS_PORT)
    
    def wipe_players(self):
        self.rsps.wipe_all_players()

# ============================================================================
# Discord Bot Cog
# ============================================================================
class CloutScapeBot(commands.Cog):
    """Enhanced CloutScape bot with RSPS integration"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_file = 'server_config.json'
        self.setup_status = {}
        # Initialize systems
        try:
            self.gambling = GamblingSystem()
            self.pvp = PvPSystem()
            self.events = EventSystem()
            self.rewards = RewardSystem()
            self.webhooks = WebhookManager()
            self.rsps_manager = RSPSManager()
        except Exception as e:
            logger.error(f"Error initializing systems: {e}")
            raise
        self.load_configs()

    def cog_load(self):
        self.update_server_status.start()
        self.update_leaderboards.start()

    def cog_unload(self):
        self.update_server_status.cancel()
        self.update_leaderboards.cancel()

    def load_configs(self):
        """Load saved server configurations"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.setup_status = json.load(f)
                logger.info(f"Loaded configurations for {len(self.setup_status)} servers")
            else:
                self.setup_status = {}
        except Exception as e:
            logger.error(f"Error loading configs: {e}")

    def save_configs(self):
        """Save server configurations"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.setup_status, f, indent=2)
            logger.info("Configurations saved")
        except Exception as e:
            logger.error(f"Error saving configs: {e}")

    @tasks.loop(minutes=5)
    async def update_server_status(self):
        """Update server status channel"""
        try:
            for guild in self.bot.guilds:
                status_channel = discord.utils.get(guild.text_channels, name='server-status')
                if status_channel:
                    status = self.rsps_manager.rsps.get_server_status()
                    players = self.rsps_manager.rsps.get_all_players()
                    embed = discord.Embed(
                        title="📊 CloutScape Server Status",
                        description="Real-time server statistics",
                        color=discord.Color.green() if status['online'] else discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="🟢 Server Status", value="Online" if status['online'] else "Offline", inline=True)
                    embed.add_field(name="👥 Players Online", value=f"{status['players_online']}/{status['max_players']}", inline=True)
                    embed.add_field(name="⏱️ Uptime", value=status['uptime'], inline=True)
                    embed.add_field(name="📝 Total Registered", value=str(len(players)), inline=True)
                    embed.add_field(name="🎮 Version", value=status['version'], inline=True)
                    embed.add_field(name="🌐 Connect", value=Config.CLOUDFLARE_DOMAIN, inline=True)
                    embed.set_footer(text="Updates every 5 minutes")
                    async for message in status_channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                    await status_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error updating server status: {e}")

    @update_server_status.before_loop
    async def before_update_server_status(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=10)
    async def update_leaderboards(self):
        """Update leaderboards channel"""
        try:
            for guild in self.bot.guilds:
                lb_channel = discord.utils.get(guild.text_channels, name='leaderboards')
                if lb_channel:
                    gp_leaders = self.rsps_manager.rsps.get_leaderboard('gp_balance', 10)
                    embed = discord.Embed(
                        title="🏆 CloutScape Leaderboards",
                        description="Top players in CloutScape",
                        color=discord.Color.gold(),
                        timestamp=datetime.now()
                    )
                    if gp_leaders:
                        gp_text = ""
                        medals = ["🥇", "🥈", "🥉"]
                        for i, player in enumerate(gp_leaders):
                            medal = medals[i] if i < 3 else f"{i+1}."
                            gp_text += f"{medal} **{player['username']}** - {player['gp_balance']:,} GP\n"
                        embed.add_field(name="💰 Richest Players", value=gp_text, inline=False)
                    login_leaders = self.rsps_manager.rsps.get_leaderboard('total_logins', 5)
                    if login_leaders:
                        login_text = ""
                        for i, player in enumerate(login_leaders):
                            login_text += f"{i+1}. **{player['username']}** - {player['total_logins']} logins\n"
                        embed.add_field(name="🎮 Most Active Players", value=login_text, inline=False)
                    embed.set_footer(text="Updates every 10 minutes")
                    async for message in lb_channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                    await lb_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error updating leaderboards: {e}")

    @update_leaderboards.before_loop
    async def before_update_leaderboards(self):
        await self.bot.wait_until_ready()

    # ────────────────────── Commands ──────────────────────

    @commands.command(name='register')
    async def register(self, ctx, username: str = None):
        """Register a new RSPS account"""
        try:
            if not username:
                await ctx.send("❌ Please provide a username! Example: `!register YourName`")
                return
            result = self.rsps_manager.rsps.register_player(str(ctx.author.id), str(ctx.author), username)
            if result['success']:
                embed = discord.Embed(title="✅ Account Created!", description=f"Welcome, **{username}**!", color=discord.Color.green())
                embed.add_field(name="Username", value=f"`{result['username']}`", inline=False)
                embed.add_field(name="Password", value=f"||`{result['password']}`||", inline=False)
                embed.add_field(name="Important", value="Save your credentials!", inline=False)
                embed.add_field(name="Download Client", value=f"[Click here]({Config.CLIENT_DOWNLOAD_URL})", inline=False)
                embed.add_field(name="Server Address", value=f"`{Config.CLOUDFLARE_DOMAIN}`", inline=False)
                embed.add_field(name="How to Play", value="1. Download\n2. Run jar\n3. Login\n4. Play", inline=False)
                try:
                    await ctx.author.send(embed=embed)
                    await ctx.send(f"✅ Account created! DM sent, {ctx.author.mention}")
                except discord.Forbidden:
                    await ctx.send(f"✅ Account created, but I couldn't DM you! **Password:** ||`{result['password']}`||")
                
                member_role = discord.utils.get(ctx.guild.roles, name='Member')
                if member_role:
                    await ctx.author.add_roles(member_role)
                logger.info(f"Registered: {username} by {ctx.author}")
            else:
                await ctx.send(f"❌ {result['error']}")
        except Exception as e:
            logger.error(f"Register error: {e}")
            await ctx.send("❌ Registration failed.")

    @commands.command(name='download')
    async def download(self, ctx):
        """Get client download link"""
        try:
            embed = discord.Embed(title="📥 Download Client", description="Start playing!", color=discord.Color.blue())
            embed.add_field(name="Link", value=f"[Download jar]({Config.CLIENT_DOWNLOAD_URL})", inline=False)
            embed.add_field(name="Requirements", value="Java 11+\nOS: Win/Mac/Linux\nAccount", inline=False)
            embed.add_field(name="Quick Start", value="Download → Run → Login → Play", inline=False)
            embed.add_field(name="No account?", value="Use !register <name>", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Download error: {e}")
            await ctx.send("❌ Download info failed.")

    @commands.command(name='stats')
    async def stats(self, ctx, member: discord.Member = None):
        """View player statistics"""
        try:
            target = member or ctx.author
            stats = self.rsps_manager.rsps.get_player_stats(str(target.id))
            if not stats:
                await ctx.send(f"❌ {target.mention} no account. Use !register.")
                return
            embed = discord.Embed(title=f"📊 Stats - {stats['username']}", color=discord.Color.blue())
            embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
            embed.add_field(name="GP Balance", value=f"{stats['gp_balance']:,} GP", inline=True)
            embed.add_field(name="Rank", value=stats['rank'], inline=True)
            embed.add_field(name="Logins", value=str(stats['total_logins']), inline=True)
            embed.add_field(name="Created", value=stats['created_at'][:10] if stats['created_at'] != 'Unknown' else 'Unknown', inline=True)
            embed.add_field(name="Last Login", value=stats['last_login'][:10] if stats['last_login'] and stats['last_login'] != 'Never' else 'Never', inline=True)
            embed.add_field(name="Status", value="Banned" if stats['is_banned'] else "Active", inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await ctx.send("❌ Stats failed.")

    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    async def leaderboard(self, ctx):
        """View top players"""
        try:
            gp_leaders = self.rsps_manager.rsps.get_leaderboard('gp_balance', 10)
            embed = discord.Embed(title="🏆 Leaderboards", description="Top GP", color=discord.Color.gold())
            if gp_leaders:
                gp_text = ""
                medals = ["🥇", "🥈", "🥉"]
                for i, player in enumerate(gp_leaders):
                    medal = medals[i] if i < 3 else f"{i+1}."
                    gp_text += f"{medal} **{player['username']}** - {player['gp_balance']:,} GP\n"
                embed.add_field(name="Richest Players", value=gp_text, inline=False)
            else:
                embed.add_field(name="Richest Players", value="No players yet!", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Leaderboard error: {e}")
            await ctx.send("❌ Leaderboard failed.")

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help message"""
        try:
            embed = discord.Embed(title="🤖 Commands", description="All commands", color=discord.Color.blue())
            embed.add_field(name="Player Commands", value="`!register <name>`\n`!download`\n`!stats [@user]`\n`!leaderboard`\n`!help`\n`!lbimage`", inline=False)
            if ctx.author.guild_permissions.administrator:
                embed.add_field(name="Admin Commands", value="`!setup`\n`!addgp <@user> <amount>`\n`!removegp <@user> <amount>`\n`!ban <@user> [reason]`\n`!unban <@user>`\n`!resetpass <@user>`\n`!broadcast <msg>`\n`!wipe`\n`!remake`\n`!role add <@user> <role>`\n`!role remove <@user> <role>`\n`!role list`", inline=False)
            embed.set_footer(text="CloutScape RSPS")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Help error: {e}")
            await ctx.send("❌ Help failed.")

    @commands.command(name='addgp')
    @commands.has_permissions(administrator=True)
    async def add_gp(self, ctx, member: discord.Member, amount: int):
        """Add GP to a player (Admin only)"""
        try:
            if self.rsps_manager.rsps.add_gp(str(member.id), amount):
                await ctx.send(f"✅ Added {amount:,} GP to {member.display_name}!")
                logger.info(f"{ctx.author} added {amount} GP to {member}")
            else:
                await ctx.send(f"❌ {member.mention} no account.")
        except Exception as e:
            logger.error(f"Addgp error: {e}")
            await ctx.send("❌ Addgp failed.")

    @commands.command(name='removegp')
    @commands.has_permissions(administrator=True)
    async def remove_gp(self, ctx, member: discord.Member, amount: int):
        """Remove GP from a player (Admin only)"""
        try:
            if self.rsps_manager.rsps.remove_gp(str(member.id), amount):
                await ctx.send(f"✅ Removed {amount:,} GP from {member.display_name}!")
                logger.info(f"{ctx.author} removed {amount} GP from {member}")
            else:
                await ctx.send("❌ Failed to remove GP.")
        except Exception as e:
            logger.error(f"Removegp error: {e}")
            await ctx.send("❌ Removegp failed.")

    @commands.command(name='ban')
    @commands.has_permissions(administrator=True)
    async def ban_player(self, ctx, member: discord.Member, *, reason: str = "Violation of rules"):
        """Ban a player (Admin only)"""
        try:
            if self.rsps_manager.rsps.ban_player(str(member.id), reason):
                await ctx.send(f"✅ Banned {member.display_name}! Reason: {reason}")
                logger.info(f"{ctx.author} banned {member}: {reason}")
            else:
                await ctx.send(f"❌ {member.mention} no account.")
        except Exception as e:
            logger.error(f"Ban error: {e}")
            await ctx.send("❌ Ban failed.")

    @commands.command(name='unban')
    @commands.has_permissions(administrator=True)
    async def unban_player(self, ctx, member: discord.Member):
        """Unban a player (Admin only)"""
        try:
            if self.rsps_manager.rsps.unban_player(str(member.id)):
                await ctx.send(f"✅ Unbanned {member.display_name}!")
                logger.info(f"{ctx.author} unbanned {member}")
            else:
                await ctx.send(f"❌ {member.mention} no account.")
        except Exception as e:
            logger.error(f"Unban error: {e}")
            await ctx.send("❌ Unban failed.")

    @commands.command(name='resetpass')
    @commands.has_permissions(administrator=True)
    async def reset_password(self, ctx, member: discord.Member):
        """Reset player password (Admin only)"""
        try:
            new_password = self.rsps_manager.rsps.reset_password(str(member.id))
            if new_password:
                try:
                    await member.send(f"🔑 Password reset: ||`{new_password}`||")
                    await ctx.send(f"✅ Password reset for {member.display_name}! DM sent.")
                    logger.info(f"{ctx.author} reset password for {member}")
                except discord.Forbidden:
                    await ctx.send(f"✅ Reset, but no DM. Password: ||`{new_password}`||")
            else:
                await ctx.send(f"❌ {member.mention} no account.")
        except Exception as e:
            logger.error(f"Resetpass error: {e}")
            await ctx.send("❌ Resetpass failed.")

    @commands.command(name='broadcast')
    @commands.has_permissions(administrator=True)
    async def broadcast(self, ctx, *, message: str):
        """Send announcement to announcements channel (Admin only)"""
        try:
            announcements = discord.utils.get(ctx.guild.text_channels, name='announcements')
            if announcements:
                embed = discord.Embed(title="📢 Announcement", description=message, color=discord.Color.red(), timestamp=datetime.now())
                embed.set_footer(text=f"By {ctx.author.display_name}")
                await announcements.send(embed=embed)
                await ctx.send("✅ Sent!")
                logger.info(f"{ctx.author} broadcast: {message}")
            else:
                await ctx.send("❌ No announcements channel.")
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            await ctx.send("❌ Broadcast failed.")

    @commands.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        """Advanced server setup with channels and roles"""
        try:
            await ctx.send("🚀 Setup starting...")
            categories = {}
            for cat_name in set(ch['category'] for ch in Config.CHANNELS.values()):
                category = discord.utils.get(ctx.guild.categories, name=cat_name)
                if not category:
                    category = await ctx.guild.create_category(cat_name)
                categories[cat_name] = category
            for role_name, role_config in Config.ROLES.items():
                existing = discord.utils.get(ctx.guild.roles, name=role_name)
                if not existing:
                    perms_dict = {p: True for p in role_config['permissions']}
                    await ctx.guild.create_role(
                        name=role_name,
                        color=role_config['color'],
                        hoist=role_config['hoist'],
                        mentionable=role_config['mentionable'],
                        permissions=Permissions(**perms_dict)
                    )
            for ch_name, ch_config in Config.CHANNELS.items():
                existing = discord.utils.get(ctx.guild.text_channels, name=ch_name)
                if not existing:
                    category = categories.get(ch_config['category'])
                    await ctx.guild.create_text_channel(name=ch_name, category=category, topic=ch_config['topic'])
            self.setup_status[str(ctx.guild.id)] = {'guild_name': ctx.guild.name, 'setup_date': datetime.now().isoformat(), 'status': 'completed'}
            self.save_configs()
            await ctx.send("✅ Setup complete!")
            logger.info(f"Setup for {ctx.guild.name}")
        except Exception as e:
            logger.error(f"Setup error: {e}")
            await ctx.send(f"❌ Setup failed: {str(e)}")

    @commands.command(name='wipe')
    @commands.has_permissions(administrator=True)
    async def wipe(self, ctx):
        """Wipe RSPS data (dangerous, admin only)"""
        try:
            msg = await ctx.send("⚠️ Wipe all data? Type 'yes' to confirm (30s).")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'yes'
            await self.bot.wait_for('message', check=check, timeout=30.0)
            self.rsps_manager.wipe_players()
            await ctx.send("✅ Wiped.")
            logger.info(f"{ctx.author} wiped data")
        except asyncio.TimeoutError:
            await ctx.send("❌ Wipe cancelled.")
        except Exception as e:
            logger.error(f"Wipe error: {e}")
            await ctx.send("❌ Wipe failed.")

    @commands.command(name='remake')
    @commands.has_permissions(administrator=True)
    async def remake(self, ctx):
        """Remake channels and roles (admin only)"""
        try:
            await self.setup(ctx)  # Reuse setup for remake
            await ctx.send("✅ Remake complete.")
        except Exception as e:
            logger.error(f"Remake error: {e}")
            await ctx.send("❌ Remake failed.")

    @commands.group(name='role')
    @commands.has_permissions(administrator=True)
    async def role(self, ctx):
        """Roles manager"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use: !role add/remove/list")

    @role.command(name='add')
    async def role_add(self, ctx, member: discord.Member, *, role_name: str):
        """Add role to user"""
        try:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                await member.add_roles(role)
                await ctx.send(f"✅ Added {role_name} to {member.mention}")
            else:
                await ctx.send(f"❌ {role_name} not found.")
        except Exception as e:
            logger.error(f"Role add error: {e}")
            await ctx.send("❌ Add failed.")

    @role.command(name='remove')
    async def role_remove(self, ctx, member: discord.Member, *, role_name: str):
        """Remove role from user"""
        try:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                await member.remove_roles(role)
                await ctx.send(f"✅ Removed {role_name} from {member.mention}")
            else:
                await ctx.send(f"❌ {role_name} not found.")
        except Exception as e:
            logger.error(f"Role remove error: {e}")
            await ctx.send("❌ Remove failed.")

    @role.command(name='list')
    async def role_list(self, ctx):
        """List roles"""
        try:
            roles = "\n".join(r.name for r in ctx.guild.roles)
            embed = discord.Embed(title="Roles List", description=roles, color=discord.Color.blue())
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Role list error: {e}")
            await ctx.send("❌ List failed.")

    @commands.command(name='lbimage')
    async def lb_image(self, ctx):
        """Image visualizer for leaderboard"""
        try:
            gp_leaders = self.rsps_manager.rsps.get_leaderboard('gp_balance', 5)
            if not gp_leaders:
                await ctx.send("❌ No leaders.")
                return
            names = [p['username'] for p in gp_leaders]
            balances = [p['gp_balance'] for p in gp_leaders]
            fig, ax = plt.subplots()
            ax.bar(names, balances)
            ax.set_title("Top GP Leaders")
            ax.set_ylabel("GP")
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            file = discord.File(buf, filename="lb.png")
            await ctx.send(file=file)
        except Exception as e:
            logger.error(f"Lbimage error: {e}")
            await ctx.send("❌ Image failed.")

# ============================================================================
# Bot Initialization
# ============================================================================
class CustomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix=Config.COMMAND_PREFIX, intents=intents, help_command=None)

    async def setup_hook(self):
        await self.add_cog(CloutScapeBot(self))
        logger.info("Cog loaded")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        logger.info(f"In {len(self.guilds)} guilds")
        await self.change_presence(activity=discord.Game(name=Config.BOT_STATUS))
        logger.info("Ready!")

    async def on_member_join(self, member):
        general = discord.utils.get(member.guild.text_channels, name='general')
        if general:
            embed = discord.Embed(
                title=f"Welcome {member.display_name}!",
                description="Get started with !register",
                color=discord.Color.green()
            )
            await general.send(embed=embed)

def main():
    if not Config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is missing")
        sys.exit(1)

    bot = CustomBot()

    try:
        bot.run(Config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid token — check DISCORD_TOKEN")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Bot startup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
