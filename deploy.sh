#!/bin/bash

# CloutScape Pro - Automated VPS Deployment Script
# Usage: curl -sSL https://raw.githubusercontent.com/No6love9/CloutScape-Pro/main/deploy.sh | bash

set -e

echo "🚀 Starting CloutScape Deployment..."

# 1. Update System
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y docker.io docker-compose git curl

# 2. Clone Repository (if not already present)
if [ ! -d "CloutScape-Pro" ]; then
    git clone https://github.com/No6love9/CloutScape-Pro.git
fi

cd CloutScape-Pro/platform

# 3. Setup Environment
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Creating from example..."
    cp .env.example .env
    echo "❌ Please edit CloutScape-Pro/platform/.env with your production secrets and run this script again."
    exit 1
fi

# 4. Create SSL directory for Cloudflare Origin Certificates
mkdir -p ssl
if [ ! -f "ssl/cloutscape.crt" ]; then
    echo "ℹ️ Cloudflare SSL certificates not found in platform/ssl/"
    echo "ℹ️ Please place cloutscape.crt and cloutscape.key in platform/ssl/ for HTTPS."
fi

# 5. Build and Start Containers
echo "📦 Building Docker containers..."
sudo docker-compose --profile production build
sudo docker-compose --profile production up -d

# 6. Run Database Migrations
echo "🗄️ Running database migrations..."
sudo docker-compose exec -T web flask db upgrade || echo "Migrations skipped or already up to date."

echo "✅ Deployment Complete!"
echo "🌐 Your website should be live at https://cloutscape.org"
echo "📊 Monitor logs with: docker-compose logs -f"
