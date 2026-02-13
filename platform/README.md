# CloutScape Platform - Web Application

The ultimate OSRS gambling community and gold trading platform with live price comparison, Discord/Telegram integration, and automated price intelligence.

## 🎯 Features

### Public Website
- **Landing Page** with animated gold particles and hero section
- **Live Price Ticker** showing current USD per 1M GP rates
- **Interactive Price Comparison** with real-time competitor data
- **GP Calculator** with slider to calculate savings
- **Community Integration** with Discord/Telegram member counts
- **Responsive Design** with dark theme and gold/cyan accents

### Backend Systems
- **Flask Web Framework** with SQLAlchemy ORM
- **PostgreSQL Database** for persistent storage
- **Redis Cache** for real-time data and rate limiting
- **WebSocket Support** for live price updates
- **Discord OAuth2** authentication
- **RESTful API** with rate limiting and CAPTCHA protection

### Price Intelligence Engine
- **Automated Scraping** with Playwright (stealth mode)
- **Multi-Competitor Tracking** (PlayerAuctions, Sythe, OSRS Exchange, Eldorado, RPGStash)
- **Smart Price Calculation** with outlier removal (IQR method)
- **Dynamic Pricing** (15% below median, respects cost floor)
- **Historical Data** tracking and visualization

### Discord Bot
- `/price` - Show current GP rates
- `/leaderboard` - Display top clout points
- `/stake` - Log gambling results
- `/referral` - Get referral link
- **Webhooks** for price alerts and order notifications

### Telegram Bot (Optional)
- `/start` - Welcome message
- `/price` - Check current rates
- **Broadcast Channel** for announcements

### Admin Dashboard
- **Live Price Monitor** with manual override capability
- **Order Management** with status updates
- **User Management** with clout points and referrals
- **Gambling Logs** approval system
- **Real-time Log Viewer**

## 📁 Project Structure

```
platform/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes/
│   │   ├── main.py              # Public routes
│   │   ├── api.py               # API endpoints
│   │   ├── auth.py              # Discord OAuth
│   │   └── admin.py             # Admin routes
│   ├── services/
│   │   ├── price_fetcher.py     # Scraping & price logic
│   │   ├── price_scheduler.py   # Scheduled price updates
│   │   ├── discord_bot.py       # Discord bot
│   │   ├── telegram_bot.py      # Telegram bot
│   │   ├── webhook.py           # Discord webhooks
│   │   └── socketio.py          # WebSocket events
│   ├── static/
│   │   ├── css/style.css        # Custom CSS
│   │   ├── js/
│   │   │   ├── price-updates.js # Live price updates
│   │   │   ├── calculator.js    # GP calculator
│   │   │   └── main.js          # General JS
│   │   └── images/              # Static images
│   ├── templates/
│   │   ├── base.html            # Base template
│   │   ├── index.html           # Homepage
│   │   └── admin/               # Admin templates
│   └── utils/
│       ├── security.py          # Auth & CAPTCHA
│       ├── helpers.py           # Utility functions
│       └── logger.py            # Logging config
├── migrations/                  # Database migrations
├── tests/                       # Unit tests
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Container image
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── run.py                       # Application entry point
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Discord Application (for OAuth and bot)
- reCAPTCHA keys (optional)
- Telegram Bot Token (optional)

### 1. Clone Repository
```bash
cd /path/to/CloutScape-Pro/platform
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `SECRET_KEY` - Flask secret key
- `POSTGRES_PASSWORD` - Database password
- `DISCORD_CLIENT_ID` - Discord OAuth client ID
- `DISCORD_CLIENT_SECRET` - Discord OAuth secret
- `DISCORD_BOT_TOKEN` - Discord bot token
- `ADMIN_USERNAME` - Admin panel username
- `ADMIN_PASSWORD` - Admin panel password

### 3. Start Services
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Flask web app (port 5000)
- Discord bot
- Price scraper

### 4. Initialize Database
```bash
docker-compose exec web flask db upgrade
```

### 5. Access Application
- **Website**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin
- **API**: http://localhost:5000/api/v1/

## 🔧 Development Setup

### Local Development (without Docker)

1. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Set Up Database**
```bash
# Install PostgreSQL locally or use Docker for just the database
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=cloutscape postgres:15-alpine

# Run migrations
flask db upgrade
```

4. **Start Redis**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

5. **Run Application**
```bash
python run.py
```

## 📊 Database Schema

### Users Table
- `id` - UUID primary key
- `discord_id` - Discord user ID
- `username` - Display name
- `email` - Email address
- `clout_points` - Gamification points
- `referral_code` - Unique referral code
- `referred_by` - Referrer user ID

### Orders Table
- `id` - UUID primary key
- `user_id` - Foreign key to users
- `amount_gp` - GP amount ordered
- `price_usd` - Total price in USD
- `status` - Order status (pending/paid/processing/completed/refunded)
- `in_game_rsn` - RuneScape username

### Price Snapshots Table
- `id` - Auto-increment ID
- `competitor` - Competitor name
- `price_per_m` - Price per 1M GP
- `our_price_per_m` - Our price at that time
- `created_at` - Timestamp

### Gambling Logs Table
- `id` - UUID primary key
- `user_id` - Foreign key to users
- `game_type` - Type of game (duel/staking/flower)
- `amount_won` - GP won
- `amount_lost` - GP lost
- `approved` - Admin approval status

## 🤖 Bot Commands

### Discord Bot
- `/price` - Show current OSRS GP rates
- `/leaderboard` - Top 10 users by clout points
- `/stake <amount> <win/loss> <game>` - Log gambling result
- `/referral` - Get your referral link

### Telegram Bot
- `/start` - Welcome message
- `/price` - Check current GP rates

## 🔐 Security Features

- **Rate Limiting** - 60 requests/minute per IP on public endpoints
- **reCAPTCHA v3** - On checkout and forms
- **Discord OAuth2** - Secure authentication
- **Admin Authentication** - Separate admin login
- **HTTPS Ready** - Nginx configuration for SSL
- **Environment Variables** - No secrets in code

## 📈 Monitoring & Logs

### View Logs
```bash
# Web application logs
docker-compose logs -f web

# Discord bot logs
docker-compose logs -f discord-bot

# Price scraper logs
docker-compose logs -f price-scraper

# All services
docker-compose logs -f
```

### Database Backups
```bash
# Backup
docker-compose exec postgres pg_dump -U cloutscape cloutscape > backup.sql

# Restore
docker-compose exec -T postgres psql -U cloutscape cloutscape < backup.sql
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Test specific module
pytest tests/test_price_fetcher.py

# With coverage
pytest --cov=app tests/
```

## 🚢 Production Deployment

### 1. Update Environment
```bash
# Set production values in .env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
POSTGRES_PASSWORD=<strong-password>
ADMIN_PASSWORD=<strong-password>
```

### 2. Enable Nginx (SSL)
```bash
# Start with production profile
docker-compose --profile production up -d
```

### 3. Set Up SSL Certificates
```bash
# Place certificates in ssl/ directory
ssl/
├── certificate.crt
├── private.key
└── ca_bundle.crt
```

### 4. Configure Domain
Update `DISCORD_REDIRECT_URI` in `.env`:
```
DISCORD_REDIRECT_URI=https://cloutscape.org/auth/callback
```

## 🛠️ Troubleshooting

### Price Scraping Not Working
- Check Playwright installation: `playwright install chromium`
- Verify proxy configuration (if using)
- Check logs: `docker-compose logs price-scraper`

### Discord Bot Not Responding
- Verify `DISCORD_BOT_TOKEN` is correct
- Check bot has proper permissions in Discord server
- Ensure bot is invited with `applications.commands` scope

### Database Connection Issues
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check `DATABASE_URL` in environment
- Test connection: `docker-compose exec postgres psql -U cloutscape`

## 📝 API Documentation

### GET /api/v1/prices/live
Returns current live prices from all competitors.

**Response:**
```json
{
  "our_price": 0.85,
  "competitor_prices": {
    "PlayerAuctions": 1.00,
    "Eldorado": 0.95
  },
  "average_competitor": 0.98,
  "savings_percent": 13.3,
  "updated_at": "2026-02-13T12:00:00"
}
```

### GET /api/v1/prices/history?days=7
Returns historical price data.

### GET /api/v1/leaderboard?limit=10
Returns top users by clout points.

### POST /api/v1/orders
Create a new gold order (requires authentication).

**Request:**
```json
{
  "amount_gp": 100000000,
  "in_game_rsn": "PlayerName",
  "recaptcha_token": "..."
}
```

### GET /api/v1/orders/<order_id>
Check order status.

## 📄 License

This project is part of CloutScape Pro. All rights reserved.

## 🤝 Contributing

This is a private project. For issues or feature requests, contact the development team.

---

**Built with ❤️ for the OSRS community**
