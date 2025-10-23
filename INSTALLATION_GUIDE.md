# Flood Speed GUI - Installation Guide

## Quick Installation (Recommended)

### Step 1: Install Dependencies

```bash
# Make sure you're using Python 3.8 or higher
python --version

# Install all required packages
pip install PyQt6 opencv-python numpy matplotlib vtk h5py tqdm scipy
```

### Step 2: Install OpyFlow

```bash
# Navigate to the opyflow directory
cd /Users/worakanlasudee/Documents/GitHub/Flood_speed/opyflow

# Install in development mode
pip install -e .
```

### Step 3: Test Installation

```bash
# Test if everything is installed correctly
python -c "import opyf; import PyQt6; import cv2; import numpy; print('All packages installed successfully!')"
```

### Step 4: Launch the GUI

```bash
# Launch the Flood Speed GUI
python flood_speed_gui.py
```

## Alternative: Using Conda Environment

If you prefer using conda (recommended for cleaner dependency management):

```bash
# Create a new conda environment
conda create -n flood_analysis python=3.11

# Activate the environment
conda activate flood_analysis

# Install dependencies
conda install -c conda-forge opencv matplotlib numpy scipy vtk h5py tqdm
pip install PyQt6

# Install opyflow
cd /Users/worakanlasudee/Documents/GitHub/Flood_speed/opyflow
pip install -e .

# Launch GUI
python flood_speed_gui.py
```

## Using Virtual Environment (venv)

```bash
# Create virtual environment
cd /Users/worakanlasudee/Documents/GitHub/Flood_speed/opyflow
python -m venv flood_env

# Activate environment
# On macOS/Linux:
source flood_env/bin/activate
# On Windows:
# flood_env\Scripts\activate

# Install dependencies
pip install PyQt6 opencv-python numpy matplotlib vtk h5py tqdm scipy

# Install opyflow
pip install -e .

# Launch GUI
python flood_speed_gui.py
```

## Troubleshooting Installation

### Issue: PyQt6 import error

```bash
# Try installing PyQt6 with specific backend
pip install PyQt6 PyQt6-Qt6 PyQt6-sip
```

### Issue: OpenCV import error

```bash
# Try the headless version if you have display issues
pip uninstall opencv-python
pip install opencv-python-headless
```

### Issue: VTK installation fails

```bash
# On some systems, VTK needs to be installed via conda
conda install -c conda-forge vtk

# Or try a specific version
pip install vtk==9.2.6
```

### Issue: matplotlib backend problems

If you get matplotlib backend errors, add this to your environment:

```bash
# On macOS
export MPLBACKEND=TkAgg

# Or set it in Python before importing matplotlib
python -c "import matplotlib; matplotlib.use('TkAgg'); import matplotlib.pyplot as plt"
```

## Verifying Installation

Run this verification script:

```python
# Save as test_installation.py
import sys

print("Testing installation...")
print(f"Python version: {sys.version}")

try:
    import PyQt6
    print("✓ PyQt6 installed")
except ImportError as e:
    print(f"✗ PyQt6 missing: {e}")

try:
    import cv2
    print(f"✓ OpenCV installed (version {cv2.__version__})")
except ImportError as e:
    print(f"✗ OpenCV missing: {e}")

try:
    import numpy
    print(f"✓ NumPy installed (version {numpy.__version__})")
except ImportError as e:
    print(f"✗ NumPy missing: {e}")

try:
    import matplotlib
    print(f"✓ Matplotlib installed (version {matplotlib.__version__})")
except ImportError as e:
    print(f"✗ Matplotlib missing: {e}")

try:
    import vtk
    print(f"✓ VTK installed (version {vtk.VTK_VERSION})")
except ImportError as e:
    print(f"✗ VTK missing: {e}")

try:
    import h5py
    print(f"✓ h5py installed (version {h5py.__version__})")
except ImportError as e:
    print(f"✗ h5py missing: {e}")

try:
    import opyf
    print("✓ OpyFlow installed")
except ImportError as e:
    print(f"✗ OpyFlow missing: {e}")

print("\nInstallation check complete!")
```

Run it with:
```bash
python test_installation.py
```

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4 GB RAM
- 1 GB free disk space
- Display resolution: 1280x720

### Recommended Requirements
- Python 3.10 or 3.11
- 8 GB RAM or more
- SSD with 5 GB free space
- Display resolution: 1920x1080 or higher
- GPU (for faster video processing)

## Platform-Specific Notes

### macOS
- Works on macOS 10.14 (Mojave) and later
- On Apple Silicon (M1/M2), use native Python
- May need to install Xcode Command Line Tools: `xcode-select --install`

### Windows
- Works on Windows 10 and 11
- Visual C++ Redistributable may be required
- Use PowerShell or Command Prompt

### Linux
- Tested on Ubuntu 20.04+
- May need additional system packages:
  ```bash
  sudo apt-get install python3-dev libgl1-mesa-glx libglib2.0-0
  ```

## Running from Source

If you want to modify the code:

```bash
# Clone or navigate to the repository
cd /Users/worakanlasudee/Documents/GitHub/Flood_speed/opyflow

# Install dependencies
pip install -r requirements.txt  # if available

# Or install manually
pip install PyQt6 opencv-python numpy matplotlib vtk h5py tqdm scipy

# Install opyflow in editable mode
pip install -e .

# Run the GUI
python flood_speed_gui.py
```

## Next Steps

After successful installation:

1. Read the [User Guide](FLOOD_SPEED_GUI_README.md)
2. Try the [Example Script](example_flood_analysis.py)
3. Load your first video and start analyzing!

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting-installation) section above
2. Verify all dependencies are installed correctly
3. Check the OpyFlow documentation
4. Open an issue on GitHub with:
   - Python version (`python --version`)
   - Operating system
   - Full error message
   - Output of `pip list`

---

Happy analyzing! 🌊📊
