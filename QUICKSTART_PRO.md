# CloutScape Platform - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Navigate to Platform Directory
```bash
cd platform/
```

### Step 2: Set Up Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and configure these **required** variables:
```bash
# Generate a strong secret key
SECRET_KEY=your-random-secret-key-here

# Database password
POSTGRES_PASSWORD=your-secure-password

# Discord OAuth (create app at https://discord.com/developers/applications)
DISCORD_CLIENT_ID=your-client-id
DISCORD_CLIENT_SECRET=your-client-secret
DISCORD_REDIRECT_URI=http://localhost:5000/auth/callback

# Discord Bot (create bot in same Discord app)
DISCORD_BOT_TOKEN=your-bot-token

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
```

### Step 3: Start the Platform
```bash
docker-compose up -d
```

This will start:
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Flask web application
- ✅ Discord bot
- ✅ Price scraper (updates every 15 minutes)

### Step 4: Initialize Database
```bash
docker-compose exec web flask db init
docker-compose exec web flask db migrate -m "Initial migration"
docker-compose exec web flask db upgrade
```

### Step 5: Access Your Platform

- **Website**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin/login
  - Username: `admin` (or what you set in .env)
  - Password: (what you set in .env)
- **API**: http://localhost:5000/api/v1/prices/live

## 🎯 What You Get

### ✨ Features Ready Out of the Box

1. **Live Price Comparison**
   - Automated scraping of competitor prices
   - Real-time updates via WebSocket
   - Smart pricing algorithm (15% below average)

2. **User System**
   - Discord OAuth2 login
   - Referral codes
   - Clout points leaderboard

3. **Order Management**
   - Create and track gold orders
   - Admin approval workflow
   - Status updates

4. **Discord Bot**
   - `/price` - Check current rates
   - `/leaderboard` - View top users
   - `/stake` - Log gambling results
   - `/referral` - Get referral link

5. **Admin Dashboard**
   - Monitor all orders
   - Manage users
   - Override prices manually
   - Approve gambling logs

## 🔧 Discord Setup

### 1. Create Discord Application
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it "CloutScape"

### 2. Set Up OAuth2
1. Go to OAuth2 → General
2. Add redirect URL: `http://localhost:5000/auth/callback`
3. Copy Client ID and Client Secret to `.env`

### 3. Create Bot
1. Go to Bot section
2. Click "Add Bot"
3. Enable these intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
4. Copy bot token to `.env` as `DISCORD_BOT_TOKEN`

### 4. Invite Bot to Server
1. Go to OAuth2 → URL Generator
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - Send Messages
   - Embed Links
   - Read Message History
4. Copy URL and open in browser to invite bot

## 📊 Verify Everything Works

### Check Services Status
```bash
docker-compose ps
```

All services should show "Up" status.

### View Logs
```bash
# All services
docker-compose logs -f

# Just web app
docker-compose logs -f web

# Just Discord bot
docker-compose logs -f discord-bot
```

### Test API
```bash
curl http://localhost:5000/api/v1/prices/live
```

Should return JSON with price data.

### Test Discord Bot
In your Discord server, type:
```
/price
```

Bot should respond with current GP rates.

## 🛠️ Common Issues

### "Database connection failed"
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### "Discord bot not responding"
```bash
# Check bot logs
docker-compose logs discord-bot

# Verify bot token in .env
# Make sure bot has proper permissions in Discord server
```

### "Price scraper not working"
```bash
# Check scraper logs
docker-compose logs price-scraper

# Manually trigger price update
docker-compose exec web python -c "from app.services.price_fetcher import update_prices; update_prices()"
```

### "Can't login with Discord"
- Verify `DISCORD_REDIRECT_URI` matches exactly in Discord app settings
- Check `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET` are correct
- Make sure redirect URI is `http://localhost:5000/auth/callback` (not https)

## 🚀 Next Steps

### 1. Customize Your Platform
- Edit `app/templates/index.html` for homepage content
- Modify `app/static/css/style.css` for styling
- Update competitor list in `app/services/price_fetcher.py`

### 2. Set Up Production
- Get a domain name
- Set up SSL certificates
- Update environment variables for production
- Enable Nginx: `docker-compose --profile production up -d`

### 3. Add More Features
- Implement payment processing
- Add more Discord bot commands
- Create additional admin tools
- Build mobile app integration

## 📚 Full Documentation

See [platform/README.md](platform/README.md) for complete documentation including:
- Detailed API documentation
- Database schema
- Security features
- Production deployment
- Troubleshooting guide

## 🆘 Need Help?

1. Check the logs: `docker-compose logs -f`
2. Read the full README: `platform/README.md`
3. Verify environment variables in `.env`
4. Make sure all Docker services are running

---

**You're all set! Your CloutScape platform is now running! 🎉**
