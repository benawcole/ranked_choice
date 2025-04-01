#!/bin/bash
cd "$(dirname "$0")"

# Define virtual environment directory
VENV_DIR="venv"

# Check if virtual environment exists, if not, create one
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
pip install -r requirements.txt

# Run the script
echo "Launching main.py..."
python main.py