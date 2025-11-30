#!/bin/bash

# Linear Gantt Chart Visualizer - Run Script
# This script sets up and runs the application

set -e  # Exit on error

echo "🚀 Linear Gantt Chart Visualizer Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your Linear API key!"
    echo "   Get your API key from: https://linear.app/settings/api"
    echo ""
    read -p "Press Enter once you've added your API key to .env, or Ctrl+C to exit..."
else
    echo "✓ .env file exists"
fi
echo ""

# Check if API key is set (basic check)
if grep -q "your_api_key_here" .env; then
    echo "⚠️  WARNING: It looks like you haven't updated your LINEAR_API_KEY in .env"
    echo "   The application may not work without a valid API key."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please update .env with your Linear API key."
        exit 1
    fi
fi

# Run the Streamlit app
echo "🎯 Starting Streamlit application..."
echo "   The app will open in your browser at http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
