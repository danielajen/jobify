#!/bin/bash

echo "🚀 Deploying JobSwipe to Heroku"

# Use existing app
app_name="jobswipe-app"
echo "Using existing Heroku app: $app_name"

# Check if app exists
if ! heroku apps:info --app $app_name > /dev/null 2>&1; then
    echo "❌ App $app_name not found. Please create it first or check the name."
    exit 1
fi

echo "✅ Found existing app: $app_name"

# Add PostgreSQL if not already added
echo "📦 Checking PostgreSQL database..."
if ! heroku addons:info --app $app_name | grep -q "postgresql"; then
    echo "Adding PostgreSQL database..."
    heroku addons:create heroku-postgresql:mini --app $app_name
else
    echo "PostgreSQL already exists"
fi

# Set environment variables
echo "🔧 Setting environment variables..."

# LinkedIn OAuth
heroku config:set LINKEDIN_CLIENT_ID="78410ucd7xak42" --app $app_name
heroku config:set LINKEDIN_CLIENT_SECRET="WPL_AP1.UXNA3HdvDRzqx702.2tvvkg==" --app $app_name
heroku config:set LINKEDIN_REDIRECT_URI="https://$app_name.herokuapp.com/linkedin/callback" --app $app_name

# Other required variables
heroku config:set SECRET_KEY="jobswipe-super-secret-key-2024-xyz123" --app $app_name
heroku config:set FLASK_ENV="production" --app $app_name

# Optional: Set these if you have them
echo "Do you have OpenAI API key? (y/n):"
read has_openai
if [ "$has_openai" = "y" ]; then
    echo "Enter your OpenAI API key:"
    read openai_key
    heroku config:set OPENAI_API_KEY="$openai_key" --app $app_name
fi

echo "Do you have SendGrid API key? (y/n):"
read has_sendgrid
if [ "$has_sendgrid" = "y" ]; then
    echo "Enter your SendGrid API key:"
    read sendgrid_key
    heroku config:set SENDGRID_API_KEY="$sendgrid_key" --app $app_name
fi

# Deploy
echo "🚀 Deploying to Heroku..."
git push heroku main

# Open the app
echo "🌐 Opening your app..."
heroku open --app $app_name

echo "✅ Deployment complete!"
echo "🔗 Your app is available at: https://$app_name.herokuapp.com"
echo "📱 LinkedIn redirect URL: https://$app_name.herokuapp.com/linkedin/callback"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://www.linkedin.com/developers/apps/78410ucd7xak42"
echo "2. Update OAuth 2.0 settings"
echo "3. Add redirect URL: https://jobswipe-app.herokuapp.com/linkedin/callback"
echo "4. Save changes" 