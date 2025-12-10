#!/bin/bash
# Setup script for Herodo Automated

echo "Setting up Herodo Automated..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "python3-venv is not installed. Installing..."
    sudo apt install python3-venv -y
fi

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

echo ""
echo "✓ Setup complete!"
echo ""
echo "To use the pipeline:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run: python -m src.main \"Your Wikipedia Article\""
echo ""


