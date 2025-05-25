#!/bin/bash

# Setup script for browser-use microservice
set -e

echo "🚀 Setting up browser-use microservice..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$SCRIPT_DIR"

# Install Node.js and PM2 if not installed
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install node
        else
            echo "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
fi

# Install PM2 globally if not installed
if ! command -v pm2 &> /dev/null; then
    echo "Installing PM2..."
    npm install -g pm2
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install browser-use from local source in development mode
echo "Installing browser-use from local source..."
pip install -e "$PROJECT_DIR"

# Install playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install chromium

# Create logs directory
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before starting the service"
fi

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start the service: pm2 start ecosystem.config.js"
echo "3. Check status: pm2 status"
echo "4. View logs: pm2 logs browser-use-api"
