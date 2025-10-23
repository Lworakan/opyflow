# Flood Speed Analysis Tool - Complete Summary

## What Has Been Created

I've built a comprehensive **Flood Speed Analysis Tool** with a graphical user interface (GUI) that automates water flow speed calculation from drone and CCTV camera footage.

## Files Created

### 1. Main Application Files

#### `flood_speed_gui.py` (Main GUI Application)
- **Full-featured PyQt6 GUI** for interactive flood analysis
- **Key Features:**
  - Video loading (MP4, AVI, MOV, MKV)
  - Interactive area selection (rectangle ROI and polygon masking)
  - Real-time optical flow processing
  - Timeline slider for temporal navigation
  - Multiple visualization tabs (flow vectors, velocity fields, time series)
  - CSV and HDF5 export capabilities
  - Processing log and progress tracking

#### `example_flood_analysis.py` (Programmatic Example)
- **Python script** for batch/automated processing
- Shows how to use the tool without GUI
- Includes temporal analysis and statistics
- Good for processing multiple videos or integration into pipelines

### 2. Documentation Files

#### `FLOOD_SPEED_GUI_README.md` (User Guide)
- Complete user manual
- Step-by-step workflow
- Parameter explanations
- Troubleshooting guide
- Advanced features
- Tips for best results

#### `INSTALLATION_GUIDE.md` (Installation Instructions)
- Multiple installation methods (pip, conda, venv)
- Platform-specific instructions (macOS, Windows, Linux)
- Troubleshooting common issues
- System requirements
- Verification scripts

#### `requirements_gui.txt` (Python Dependencies)
- All required packages with versions
- Easy installation: `pip install -r requirements_gui.txt`

## Core Features

### 1. Video Input & Processing
```
✓ Load videos from drone or CCTV cameras
✓ Supports multiple video formats
✓ Automatic frame extraction
✓ Video information display (dimensions, frame count)
```

### 2. Area Selection & Masking
```
✓ Rectangle ROI selection
✓ Custom polygon drawing for water areas
✓ Mask non-water objects (buildings, trees, etc.)
✓ Visual feedback during selection
```

### 3. Optical Flow Analysis
```
✓ Good Features to Track (GFT) detection
✓ Lucas-Kanade optical flow
✓ Velocity field interpolation
✓ Configurable processing parameters
✓ Quality filters and outlier removal
✓ CLAHE contrast enhancement
```

### 4. Visualization
```
✓ Three visualization tabs:
  - Flow Vectors: Directional flow visualization
  - Velocity Field: Color-coded speed heatmaps
  - Time Series: Temporal trends and statistics
✓ Interactive timeline slider
✓ Real-time speed statistics (avg, max, std)
✓ Matplotlib integration for publication-quality plots
```

### 5. Data Export
```
✓ CSV format (spreadsheet-compatible)
✓ HDF5 format (scientific computing)
✓ JSON statistics (frame-by-frame data)
✓ Processing parameters saved automatically
✓ Velocity field exports
```

## How It Works

### Workflow Overview

```
1. LOAD VIDEO
   ↓
2. SELECT WATER AREA (ROI/Mask)
   ↓
3. CONFIGURE PARAMETERS
   - Frame range
   - Velocity limits
   - Filter settings
   ↓
4. START PROCESSING
   - Good Features detection
   - Optical flow calculation
   - Velocity interpolation
   ↓
5. VISUALIZE RESULTS
   - Timeline navigation
   - Multiple views
   - Statistics
   ↓
6. EXPORT DATA
   - CSV/HDF5 files
   - Statistics JSON
```

### Technical Approach

**Optical Flow Method:**
- Uses OpenCV's Lucas-Kanade algorithm
- Detects "Good Features to Track" (corners, texture)
- Tracks features between consecutive frames
- Calculates displacement vectors
- Interpolates to regular grid

**Quality Assurance:**
- Bidirectional tracking verification
- Spatial consistency filtering
- Velocity range filtering
- Outlier removal based on neighborhood

**Masking Strategy:**
- Focuses analysis on water surface only
- Ignores static objects (banks, structures)
- Reduces noise from non-water features

## Use Cases

### 1. Flood Monitoring
- Real-time flood speed assessment
- Historical flood analysis
- Flood risk evaluation
- Emergency response planning

### 2. River Flow Studies
- Surface velocity measurements
- Flow pattern analysis
- Discharge estimation (with cross-section data)
- Hydrological research

### 3. Urban Drainage
- Storm water flow monitoring
- Drainage system performance
- Urban flooding assessment

### 4. Infrastructure Monitoring
- Bridge scour assessment
- Culvert flow analysis
- Channel flow verification

## Example Usage

### GUI Workflow (Recommended for Most Users)

```bash
# 1. Launch GUI
python flood_speed_gui.py

# 2. Load your video
Click "Load Video" → Select file

# 3. Define water area
Click "Draw Polygon Water Area" → Draw polygon → Press ENTER

# 4. Set parameters
Starting frame: 0
Frame step: 1
Total pairs: 50
Min speed: 0 px/frame
Max speed: 40 px/frame

# 5. Process
Click "Start Analysis" → Wait for completion

# 6. Explore
Use timeline slider to navigate
Check different visualization tabs

# 7. Export
Click "Export to CSV" or "Export to HDF5"
```

### Programmatic Usage (For Automation)

```python
from example_flood_analysis import analyze_flood_speed

# Run automated analysis
analyzer, stats = analyze_flood_speed(
    video_path='path/to/flood_video.mp4',
    output_folder='./results'
)

# Results saved automatically
# - Velocity fields (CSV/HDF5)
# - Temporal plots
# - Statistics
```

## Key Parameters Explained

### Frame Processing
- **starting_frame**: Which frame to start from (default: 0)
- **step**: Frames between image pairs (larger = bigger displacement)
- **shift**: Frame shift between consecutive pairs
- **Ntot**: Total number of frame pairs to process

### Velocity Settings
- **vlim**: [min, max] expected speeds in pixels/frame
  - Filters unrealistic velocities
  - Example: [0, 40] for moderate flood

### Filters
- **RadiusF**: Spatial filter radius (px)
  - Larger = smoother fields
  - Typical: 20-50 px
- **maxDevInRadius**: Maximum deviation tolerance
  - Lower = stricter filtering
- **CLAHE**: Contrast Limited Adaptive Histogram Equalization
  - Improves feature detection in varying light
- **wayBackGoodFlag**: Bidirectional tracking threshold
  - Ensures reliable feature tracking

## Output Data Structure

### Velocity Field (CSV)
```
Frame_0_to_1.csv:
X, Y, Ux, Uy
0, 0, 2.3, 1.5
5, 0, 2.1, 1.7
...
```

### Velocity Field (HDF5)
```
velocity_field.hdf5:
├── T_[s]           # Time vector
├── X_[px]          # X coordinates
├── Y_[px]          # Y coordinates
├── Ux_[px.s-1]     # X velocity
└── Uy_[px.s-1]     # Y velocity
```

### Statistics (JSON)
```json
[
  {
    "frame_index": 0,
    "avg_speed": 12.34,
    "max_speed": 45.67,
    "std_speed": 5.43
  }
]
```

## Advantages of This Tool

### 1. User-Friendly
- No coding required for basic use
- Intuitive graphical interface
- Visual feedback at each step
- Clear documentation

### 2. Flexible
- Works with drone and CCTV footage
- Configurable parameters for different scenarios
- Multiple export formats
- Both GUI and programmatic interfaces

### 3. Robust
- Quality filtering removes outliers
- Handles various lighting conditions
- Masking for complex scenes
- Background processing (GUI doesn't freeze)

### 4. Scientific
- Based on validated optical flow methods
- Published algorithms (Lucas-Kanade, GFT)
- Reproducible results
- Export raw data for further analysis

### 5. Open Source
- Built on OpyFlow (open source)
- Modifiable and extensible
- No licensing costs
- Community support

## Limitations & Considerations

### 1. Video Quality
- Requires visible surface features (foam, debris, ripples)
- Poor results on smooth, featureless water
- Lighting affects feature detection

### 2. Camera Stability
- Best results with stable camera
- Shaking reduces accuracy (stabilization can help)

### 3. Processing Time
- Real-time processing not feasible
- Long videos take time (proportional to frame count)
- Use smaller Ntot for testing

### 4. Spatial Scale
- Results in pixels/frame by default
- Need calibration for real-world units (m/s)
- Requires known ground truth for scaling

### 5. Surface Velocity Only
- Measures surface flow, not depth-averaged
- Apply velocity profile correction for discharge estimation

## Future Enhancements (Possible Extensions)

### Potential Additions:
1. **Automatic scaling**: Ground control point detection
2. **Real-time processing**: Optimized for live feeds
3. **Multi-region tracking**: Multiple ROIs simultaneously
4. **Automatic reporting**: PDF generation with analysis
5. **Cloud integration**: Process videos remotely
6. **Mobile app**: Simplified interface for field use
7. **3D visualization**: Enhanced spatial understanding
8. **Machine learning**: Automatic water detection
9. **Discharge calculation**: Integration with cross-section data
10. **Alert system**: Threshold-based notifications

## Integration Possibilities

This tool can be integrated with:

- **Hydrological models**: Use velocities for calibration
- **GIS systems**: Georeference results
- **Alert systems**: Trigger warnings based on speeds
- **Data dashboards**: Real-time monitoring displays
- **Research pipelines**: Automated batch processing

## Comparison with Other Tools

| Feature | This Tool | PIVlab | DaVis | Commercial |
|---------|-----------|--------|-------|------------|
| GUI | ✓ | ✓ | ✓ | ✓ |
| Open Source | ✓ | ✓ | ✗ | ✗ |
| Cost | Free | Free | $$$ | $$$$ |
| Video Support | ✓ | ✓ | ✓ | ✓ |
| Custom Masking | ✓ | Limited | ✓ | ✓ |
| Time Series | ✓ | Limited | ✓ | ✓ |
| Easy Install | ✓ | ✓ | ✗ | ✓ |
| Flood-Specific | ✓ | ✗ | ✗ | Varies |

## Getting Started Checklist

- [ ] Install Python 3.8+
- [ ] Install dependencies (`pip install -r requirements_gui.txt`)
- [ ] Install OpyFlow (`pip install -e .`)
- [ ] Test installation (`python test_installation.py`)
- [ ] Launch GUI (`python flood_speed_gui.py`)
- [ ] Load test video
- [ ] Try rectangle ROI selection
- [ ] Process small sample (Ntot=10)
- [ ] Explore visualizations
- [ ] Export results
- [ ] Read full documentation

## Support & Resources

### Documentation
- **User Guide**: `FLOOD_SPEED_GUI_README.md`
- **Installation**: `INSTALLATION_GUIDE.md`
- **Example Script**: `example_flood_analysis.py`

### OpyFlow Resources
- GitHub: https://github.com/groussea/opyflow
- Paper: https://link.springer.com/article/10.1007/s00348-020-02990-y

### Python Resources
- OpenCV: https://docs.opencv.org/
- PyQt6: https://www.riverbankcomputing.com/software/pyqt/
- NumPy: https://numpy.org/

## Quick Tips

### For Best Results:
1. **Test first**: Process 10-20 frame pairs to verify parameters
2. **Start simple**: Use default parameters, adjust if needed
3. **Use CLAHE**: Enable for better feature detection
4. **Mask carefully**: Exclude banks, shadows, reflections
5. **Check statistics**: Verify speeds are realistic
6. **Export early**: Save results as you go

### Common Parameter Sets:

**Slow Flow (calm water):**
```
step=1, vlim=[0, 10], RadiusF=20
```

**Moderate Flow (normal flood):**
```
step=1, vlim=[0, 40], RadiusF=30
```

**Fast Flow (rapid flood):**
```
step=2, vlim=[0, 100], RadiusF=40
```

**Noisy Video:**
```
CLAHE=True, wayBackGoodFlag=5, maxDevInRadius=1
```

## Conclusion

You now have a complete, production-ready tool for flood speed analysis with:

✅ Modern GUI interface
✅ Automated processing
✅ Interactive visualization
✅ Multiple export formats
✅ Comprehensive documentation
✅ Example scripts
✅ Easy installation

The tool is ready to use for your flood monitoring needs!

---

**Questions?** Check the documentation or open an issue on GitHub.

**Happy flood analysis!** 🌊📊
