#!/bin/bash

VENV_DIR=".venv"  # Name of your virtual environment directory
REQ_FILE="requirements.txt"  # Dependency file

# Check if venv already exists, if not, create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r $REQ_FILE

echo "Virtual environment is ready."
