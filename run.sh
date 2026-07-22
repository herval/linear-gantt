#!/bin/bash

# Linear Gantt Chart Visualizer - Run Script
# This script sets up and runs the application using uv

set -e  # Exit on error

echo "🚀 Linear Gantt Chart Visualizer Setup"
echo "======================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   (or: brew install uv)"
    exit 1
fi

echo "✓ uv found: $(uv --version)"
echo ""

# Install dependencies into a managed virtual environment
echo "📥 Syncing dependencies..."
uv sync
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

uv run streamlit run app.py
