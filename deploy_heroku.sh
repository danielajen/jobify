#!/bin/bash

echo "🚀 Deploying JobSwipe to Heroku"

# Get app name from user
echo "Enter your Heroku app name (or press Enter to create a new one):"
read app_name

if [ -z "$app_name" ]; then
    echo "Creating new Heroku app..."
    heroku create
    app_name=$(heroku apps:info --json | jq -r '.app.name')
    echo "Created app: $app_name"
else
    echo "Using existing app: $app_name"
fi

# Add PostgreSQL
echo "📦 Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini

# Set environment variables
echo "🔧 Setting environment variables..."

# LinkedIn OAuth
heroku config:set LINKEDIN_CLIENT_ID="78410ucd7xak42"
heroku config:set LINKEDIN_CLIENT_SECRET="WPL_AP1.UXNA3HdvDRzqx702.2tvvkg=="
heroku config:set LINKEDIN_REDIRECT_URI="https://$app_name.herokuapp.com/linkedin/callback"

# Other required variables
heroku config:set SECRET_KEY="jobswipe-super-secret-key-2024-xyz123"
heroku config:set FLASK_ENV="production"

# Optional: Set these if you have them
echo "Do you have OpenAI API key? (y/n):"
read has_openai
if [ "$has_openai" = "y" ]; then
    echo "Enter your OpenAI API key:"
    read openai_key
    heroku config:set OPENAI_API_KEY="$openai_key"
fi

echo "Do you have SendGrid API key? (y/n):"
read has_sendgrid
if [ "$has_sendgrid" = "y" ]; then
    echo "Enter your SendGrid API key:"
    read sendgrid_key
    heroku config:set SENDGRID_API_KEY="$sendgrid_key"
fi

# Deploy
echo "🚀 Deploying to Heroku..."
git push heroku main

# Open the app
echo "🌐 Opening your app..."
heroku open

echo "✅ Deployment complete!"
echo "🔗 Your app is available at: https://$app_name.herokuapp.com"
echo "📱 Update your LinkedIn app redirect URL to: https://$app_name.herokuapp.com/linkedin/callback" 