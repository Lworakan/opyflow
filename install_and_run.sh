#!/bin/bash
# Installation and launcher script for Flood Speed Analysis GUI

echo "=========================================="
echo "  Flood Speed Analysis Tool - Setup"
echo "=========================================="
echo ""



# Step 2: Install GUI dependencies
echo "Step 2/2: Installing GUI dependencies..."
python3 -m pip install PyQt6 h5py
if [ $? -eq 0 ]; then
    echo "✓ GUI dependencies installed successfully"
else
    echo "✗ GUI dependencies installation failed"
    exit 1
fi
echo ""

echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "Launching Flood Speed Analysis GUI..."
echo ""

# Launch the GUI
python3 flood_speed_gui.py
