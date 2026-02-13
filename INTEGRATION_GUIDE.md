# CloutScape Integration Guide

This guide provides comprehensive instructions for integrating various services with the CloutScape project.

## 1. Cloudflare Pages Deployment (Static Site)
Cloudflare Pages is ideal for deploying the frontend of CloutScape.

### 1.1. Prepare for Static Deployment
We use **Frozen-Flask** to generate a static version of the Flask application.
1.  **Freeze Script**: Run `python platform/freeze.py` to generate the `build/` directory.
2.  **Build Command**: In Cloudflare Pages, use:
    ```bash
    pip install -r platform/requirements.txt && python platform/freeze.py
    ```
3.  **Output Directory**: Set to `build`.

### 1.2. Custom Domain
Point `cloutscape.org` to your Cloudflare Pages project in the Cloudflare dashboard.

---

## 2. Telegram Bot Setup
The Telegram bot handles price checks, reward claims, and admin notifications.

### 2.1. Creation
1.  Message [@BotFather](https://t.me/botfather) on Telegram.
2.  Use `/newbot` to create your bot and get the **API Token**.
3.  Get your **Admin Chat ID** (use [@userinfobot](https://t.me/userinfobot)).

### 2.2. Commands
- `/start`: Welcome message.
- `/price`: Live OSRS GP rates.
- `/reward`: Claim purchase rewards (generates a unique code).

---

## 3. Discord Bot Setup
The Discord bot provides community engagement and real-time alerts.

### 3.1. Creation
1.  Go to [Discord Developer Portal](https://discord.com/developers/applications).
2.  Create a new application and add a **Bot**.
3.  Enable **Message Content Intent** and **Server Members Intent**.
4.  Copy the **Bot Token**.

### 3.2. Commands
- `!price`: Show current GP rates.
- `!reward`: Claim rewards (ephemeral message).
- `!leaderboard`: Show top 10 clout points.

---

## 4. GitHub Actions & Webhooks
Automate notifications for commits, PRs, and issues.

### 4.1. Webhook Configuration
1.  Go to Repository Settings > Webhooks.
2.  Payload URL: `https://your-domain.com/api/v1/webhooks/github`
3.  Content type: `application/json`
4.  Secret: Set a strong `GITHUB_WEBHOOK_SECRET`.

### 4.2. GitHub Secrets
Add these to Settings > Secrets and variables > Actions:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_ADMIN_CHAT_ID`
- `DISCORD_BOT_TOKEN`
- `DISCORD_NOTIFICATION_CHANNEL_ID`
- `GITHUB_WEBHOOK_SECRET`
- `PLATFORM_WEBHOOK_URL` (Your API endpoint)

---
*Last Updated: February 2026*
