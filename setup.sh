#!/bin/bash
# Setup script for GenAI Document Assistant

echo "==================================="
echo "GenAI Document Assistant Setup"
echo "==================================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data/chroma
mkdir -p temp_uploads

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your LLM_API_KEY"
    echo ""
else
    echo ".env file already exists"
fi

echo ""
echo "==================================="
echo "Setup complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your LLM_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run API: ./run_api.sh"
echo "4. Run UI (in new terminal): ./run_ui.sh"
echo ""
