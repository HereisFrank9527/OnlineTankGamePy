#!/bin/bash

# Quick start script for development

set -e

echo "🚀 Starting FastAPI Backend..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your settings."
    echo ""
fi

# Check if Poetry is available
if command -v poetry &> /dev/null; then
    echo "📦 Using Poetry for dependency management..."
    
    # Install dependencies if needed
    if [ ! -d ".venv" ]; then
        echo "Installing dependencies..."
        poetry install
    fi
    
    # Run the server
    echo ""
    echo "🌟 Starting Uvicorn server with hot reload..."
    echo "📍 Server will be available at: http://localhost:8000"
    echo "📚 API docs: http://localhost:8000/docs"
    echo ""
    poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "📦 Poetry not found. Using pip..."
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Run the server
    echo ""
    echo "🌟 Starting Uvicorn server with hot reload..."
    echo "📍 Server will be available at: http://localhost:8000"
    echo "📚 API docs: http://localhost:8000/docs"
    echo ""
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi
