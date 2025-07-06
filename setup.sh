#!/bin/bash

# TailorTalk Booking Agent - Setup and Run Script

echo "🚀 Starting TailorTalk Booking Agent Setup..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
pip install -r frontend/requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your configuration before running the application."
fi

# Check for Google credentials
if [ ! -f "credentials/service-account-key.json" ]; then
    echo "⚠️ Warning: Google Calendar credentials not found."
    echo "   Please place your service-account-key.json file in the credentials/ folder."
    echo "   See credentials/.gitkeep for instructions."
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   1. Edit .env file with your API keys and configuration"
echo "   2. Add Google Calendar credentials to credentials/ folder"
echo "   3. Run: ./start.sh"
echo ""

# Make start script executable
chmod +x start.sh
