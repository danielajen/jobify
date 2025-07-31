#!/bin/bash

# Add Redis addon to Heroku
echo "Adding Redis addon to Heroku..."
heroku addons:create heroku-redis:hobby-dev --app jobswipe-app-e625703f9b1e

echo "Redis addon added successfully!"
echo "You can now deploy your app with: git push heroku main" 