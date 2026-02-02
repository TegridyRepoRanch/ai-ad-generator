#!/bin/bash
# Quick start script for AI Ad Generator

echo "🚀 AI Ad Generator - Quick Start"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your API keys:"
    echo "   - REPLICATE_API_TOKEN: Get from https://replicate.com/account/api-tokens"
    echo "   - ANTHROPIC_API_KEY: Get from https://console.anthropic.com/settings/keys"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create output directory
mkdir -p output

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server at http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

# Run the server
python3 main.py
