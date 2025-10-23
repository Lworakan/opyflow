# 🌊 Flood Speed Analysis Tool - START HERE

## What Has Been Created For You

A complete **GUI application** to automatically calculate water flow speeds from your drone or CCTV camera videos.

## ⚡ Quick Start (3 steps)

```bash
# Step 1: Launch the GUI
python flood_speed_gui.py

# Step 2: Load your video and select water area

# Step 3: Click "Start Analysis" and done!
```

That's it! Full guide: [`QUICK_START.md`](QUICK_START.md)

## 📁 What's in This Folder

| File | What It Does |
|------|--------------|
| **`flood_speed_gui.py`** | 🎯 **Main GUI application** - Launch this! |
| **`QUICK_START.md`** | 🚀 5-minute getting started guide |
| **`FLOOD_SPEED_GUI_README.md`** | 📖 Complete user manual |
| **`example_flood_analysis.py`** | 🐍 Python script example |
| **`FLOOD_SPEED_TOOL_SUMMARY.md`** | 🔬 Technical overview |
| **`INSTALLATION_GUIDE.md`** | 🔧 Installation help |
| **`requirements_gui.txt`** | 📋 Python dependencies |

## 🎯 What Can You Do?

### Analyze Flood Speeds
- Load video from drone/CCTV camera
- Select water area (ignore buildings, trees)
- Calculate flow velocities automatically
- See results in real-time

### Interactive Visualization
- Timeline slider to see speed changes
- Velocity field heatmaps
- Time series plots
- Speed statistics

### Export Results
- CSV format (Excel-compatible)
- HDF5 format (scientific analysis)
- JSON statistics
- Publication-quality plots

## 🖼️ GUI Features

### Left Panel (Controls)
1. **Video Input**: Load MP4/AVI/MOV files
2. **Area Selection**: Rectangle or polygon masking
3. **Processing Parameters**: Frame range, speed limits, filters
4. **Process Button**: Start analysis
5. **Export Options**: Save results

### Right Panel (Visualization)
1. **Flow Vectors Tab**: Directional flow visualization
2. **Velocity Field Tab**: Color heatmap of speeds
3. **Time Series Tab**: Temporal trends
4. **Timeline Slider**: Navigate through frames
5. **Speed Statistics**: Avg/Max speeds

## 📚 Documentation Guide

**New to this tool?**
→ Start with [`QUICK_START.md`](QUICK_START.md)

**Want detailed instructions?**
→ Read [`FLOOD_SPEED_GUI_README.md`](FLOOD_SPEED_GUI_README.md)

**Installation problems?**
→ Check [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md)

**Want to understand how it works?**
→ See [`FLOOD_SPEED_TOOL_SUMMARY.md`](FLOOD_SPEED_TOOL_SUMMARY.md)

**Prefer Python scripts?**
→ Use [`example_flood_analysis.py`](example_flood_analysis.py)

## ✅ System Check

Make sure you have:
- ✅ Python 3.8+ installed
- ✅ OpyFlow package (`pip install -e .`)
- ✅ PyQt5 (should be in your conda environment)
- ✅ Video file ready to analyze

## 🎬 Typical Workflow

```
1. Launch GUI
   python flood_speed_gui.py

2. Load Video
   Click "Load Video" → Select file

3. Select Area
   Click "Draw Polygon" → Draw around water → Press ENTER

4. Configure (Optional)
   Adjust parameters if needed (defaults work well!)

5. Process
   Click "Start Analysis" → Wait for completion

6. Explore
   Use timeline slider
   Check different visualization tabs

7. Export
   Click "Export to CSV" or "Export to HDF5"
```

## 💡 Quick Tips

### For Best Results:
- ✓ HD video (1080p+) with clear water surface
- ✓ Visible features on water (foam, debris, ripples)
- ✓ Stable camera position
- ✓ Good lighting conditions

### Start Simple:
- Use default parameters first
- Process 10-20 frames to test
- Adjust settings if needed
- Run full analysis once satisfied

### Mask Carefully:
- Draw polygon around ONLY water area
- Exclude banks, buildings, shadows
- This dramatically improves accuracy

## 🐛 Troubleshooting

### GUI won't launch?
The GUI has been fixed to work with PyQt5 (your environment).
Just run: `python flood_speed_gui.py`

### Missing dependencies?
```bash
pip install -e .  # Install OpyFlow
pip install PyQt5 h5py  # If needed
```

### Processing errors?
Check the log window in the GUI for details.
Most common: Mask dimension mismatch (now fixed!)

## 🎓 How It Works

**Simple Explanation:**
1. Detects trackable features on water surface
2. Follows them between frames
3. Calculates how far they moved
4. Converts to velocity
5. Creates smooth velocity field
6. Shows you the results!

**Technical:**
Uses Lucas-Kanade optical flow with Good Features to Track (GFT) detection, spatial interpolation, and quality filtering.

Based on research:
> Rousseau & Ancey (2020). Scanning PIV of turbulent flows. *Experiments in Fluids*.

## 📊 Output Formats

### CSV Files
```csv
X, Y, Ux, Uy
0, 0, 2.3, 1.5
5, 0, 2.1, 1.7
...
```

### HDF5 Files
```
velocity_field.hdf5
├── Time coordinates
├── Spatial grid (X, Y)
└── Velocity components (Ux, Uy)
```

### JSON Statistics
```json
{
  "frame_index": 0,
  "avg_speed": 12.34,
  "max_speed": 45.67
}
```

## 🎯 Use Cases

### Flood Monitoring
- Real-time flood assessment
- Historical flood analysis
- Emergency response planning
- Infrastructure risk evaluation

### River Studies
- Surface velocity measurement
- Flow pattern analysis
- Discharge estimation
- Hydrological research

### Urban Drainage
- Storm water monitoring
- Drainage performance
- Urban flooding assessment

## 🔄 Workflow Integration

The tool can be integrated with:
- GIS systems (georeferenced results)
- Hydrological models (calibration data)
- Alert systems (threshold monitoring)
- Research pipelines (batch processing)

## 📖 Learn More

### Video Tutorials
Check the example videos in `/tests/` directory

### Documentation
- User Guide: Complete instructions
- Technical Summary: How it works
- Example Scripts: Python automation

### Community
- OpyFlow GitHub: https://github.com/groussea/opyflow
- Scientific Paper: See references in docs

## 🚀 Next Actions

1. **Try it now:**
   ```bash
   python flood_speed_gui.py
   ```

2. **Read quick start:**
   Open `QUICK_START.md`

3. **Process your first video:**
   Follow the 5-minute workflow

4. **Explore advanced features:**
   Check the full user guide

5. **Automate your analysis:**
   Use `example_flood_analysis.py`

## ✨ Features Highlights

### Interactive
- ✓ Click-and-drag area selection
- ✓ Real-time visualization
- ✓ Timeline navigation
- ✓ Live statistics

### Flexible
- ✓ Multiple video formats
- ✓ Customizable parameters
- ✓ Various export options
- ✓ Batch processing capable

### Robust
- ✓ Outlier filtering
- ✓ Quality checks
- ✓ Error handling
- ✓ Progress tracking

### Open Source
- ✓ No licensing fees
- ✓ Modifiable code
- ✓ Transparent algorithms
- ✓ Community supported

## 🎉 You're Ready!

Everything is set up and working. The GUI is ready to use.

**Just run:**
```bash
python flood_speed_gui.py
```

**Questions?** Check the documentation files or the log window in the GUI.

**Happy flood analysis!** 🌊📊

---

**Version:** 1.0
**Built with:** OpyFlow • PyQt5 • OpenCV • Python
**Based on:** Peer-reviewed optical flow research
**License:** Open Source (following OpyFlow license)
