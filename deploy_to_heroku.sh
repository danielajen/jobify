#!/bin/bash

echo "🚀 Deploying JobSwipe to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "📦 Installing Heroku CLI..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Login to Heroku
echo "🔐 Logging into Heroku..."
heroku login

# Create Heroku app (if it doesn't exist)
echo "🏗️ Creating Heroku app..."
heroku create jobswipe-app --buildpack heroku/python

# Add PostgreSQL addon
echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini

# Set environment variables
echo "🔧 Setting environment variables..."
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(openssl rand -base64 32)
heroku config:set OPENAI_API_KEY=$OPENAI_API_KEY
heroku config:set SENDGRID_API_KEY=$SENDGRID_API_KEY
heroku config:set LINKEDIN_CLIENT_ID=$LINKEDIN_CLIENT_ID
heroku config:set LINKEDIN_CLIENT_SECRET=$LINKEDIN_CLIENT_SECRET

# Build frontend
echo "🌐 Building frontend..."
./build_frontend.sh

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Run database migrations
echo "🗄️ Running database migrations..."
heroku run python -c "from backend.database.db import init_db; from backend.app import app; init_db(app)"

echo "✅ Deployment complete!"
echo "🌐 Your app is live at: https://jobswipe-app.herokuapp.com" 