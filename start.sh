#!/bin/bash

# AI Job Hunter Bot - Startup Script
# This script sets up and runs the entire system

echo "🤖 AI Job Hunter Bot - Starting..."
echo ""

# Check if .env file exists
if [ ! -f "config/.env" ]; then
    echo "❌ Error: config/.env file not found!"
    echo "Please copy config/.env.example to config/.env and configure it."
    exit 1
fi

# Load environment variables
export $(cat config/.env | grep -v '#' | xargs)

echo "✅ Configuration loaded"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    echo ""
    echo "Starting with Docker Compose..."
    echo ""
    
    # Check if .env.docker exists
    if [ ! -f ".env.docker" ]; then
        echo "Creating .env.docker from config/.env..."
        cat config/.env > .env.docker
    fi
    
    # Start services
    docker-compose up -d
    
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "📝 View Logs:"
    echo "  - Bot logs: docker logs -f job_hunter_bot"
    echo "  - API logs: docker logs -f job_hunter_api"
    echo "  - DB logs: docker logs -f job_hunter_db"
    echo ""
    echo "🌐 API Available at: http://localhost:8000"
    echo "📱 Telegram Bot: Send /start to your bot"
    echo ""
else
    echo "⚠️  Docker not found. Running locally..."
    echo ""
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found! Please install Python 3.8+"
        exit 1
    fi
    
    echo "✅ Python found: $(python3 --version)"
    echo ""
    
    # Create virtual environment if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    echo "✅ Dependencies installed"
    echo ""
    
    # Start the bot
    echo "🚀 Starting AI Job Hunter Bot..."
    python run_bot.py
fi
