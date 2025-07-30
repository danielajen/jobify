#!/bin/bash

echo "🚀 Building JobSwipe Frontend for Production..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build for web
echo "🌐 Building web version..."
npx expo export --platform web

# Build for mobile
echo "📱 Building mobile versions..."
npx expo export --platform android
npx expo export --platform ios

echo "✅ Frontend build complete!"
echo "📁 Build files are in frontend/dist/" 