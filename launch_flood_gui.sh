#!/bin/bash
# Launcher script for Flood Speed Analysis GUI

echo "=========================================="
echo "  Flood Speed Analysis Tool"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if required packages are installed
echo "Checking dependencies..."

python3 -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: PyQt6 not found. Installing..."
    pip3 install PyQt6
fi

python3 -c "import opyf" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: OpyFlow not found. Installing..."
    pip3 install -e .
fi

echo "All dependencies checked!"
echo ""

# Launch the GUI
echo "Launching Flood Speed Analysis GUI..."
echo ""
python3 flood_speed_gui.py

echo ""
echo "GUI closed. Thank you for using Flood Speed Analysis Tool!"
