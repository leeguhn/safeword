#!/bin/bash

# SafeWord Quick Start Script
# This script helps set up and run the SafeWord application

set -e

echo "=========================================="
echo "SafeWord - Quick Start Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo "✓ Node.js found: $(node --version)"
echo ""

# Check for PortAudio (required for PyAudio on macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Checking for PortAudio (required for PyAudio)..."
    if ! brew list portaudio &>/dev/null; then
        echo "⚠️  PortAudio not found. Installing via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew is not installed."
            echo "Please install Homebrew from https://brew.sh/ or install PortAudio manually."
            echo ""
            echo "Alternatively, install PortAudio with:"
            echo "  brew install portaudio"
            echo ""
            echo "Then run this setup script again."
            exit 1
        fi
        brew install portaudio || {
            echo "⚠️  Failed to install PortAudio automatically."
            echo "Please install manually: brew install portaudio"
            exit 1
        }
    else
        echo "✓ PortAudio is installed"
    fi
fi

# Backend setup
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing Python dependencies..."
pip install -q --upgrade pip

# Install PyAudio separately with better error handling
echo "Installing PyAudio..."
pip install pyaudio || {
    echo ""
    echo "⚠️  PyAudio installation failed!"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS, try:"
        echo "  brew install portaudio"
        echo "  pip install pyaudio"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Ubuntu/Debian, try:"
        echo "  sudo apt-get install portaudio19-dev"
        echo "  pip install pyaudio"
    fi
    echo ""
    echo "You can continue without PyAudio, but audio recording won't work."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

echo "Installing remaining dependencies..."
pip install -q flask flask-cors python-dotenv requests psutil cryptography

echo "Installing Mycroft Precise..."
pip install -q precise-runner || echo "⚠️  Warning: Precise installation may have issues. See README for manual installation."

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

cd ..

# Frontend setup
echo ""
echo "Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

cd ..

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start backend (in terminal 1):"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   python app.py"
echo ""
echo "2. Start frontend (in terminal 2):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open browser to http://localhost:3000"
echo ""
echo "See README.md for detailed usage instructions."
echo "=========================================="
