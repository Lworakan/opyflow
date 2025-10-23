# Flood Speed Analysis GUI

An interactive graphical user interface for automated water flow speed calculation from drone and CCTV camera footage. This tool uses optical flow analysis to measure flood velocities and provides temporal visualization of flow speed changes.

## Features

### 1. Video Input Support
- **Drone footage**: Nadir (top-down) views
- **CCTV cameras**: Fixed or PTZ cameras
- **Supported formats**: MP4, AVI, MOV, MKV

### 2. Interactive Area Selection
- **Rectangle ROI**: Quick rectangular region selection
- **Polygon Masking**: Draw custom polygons around water areas
- **Static object filtering**: Automatically ignores non-water areas

### 3. Automated Flow Analysis
- **Optical flow calculation**: Lucas-Kanade method with Good Features to Track
- **Velocity field interpolation**: Smooth velocity fields on regular grids
- **Filter options**: Remove outliers and enhance accuracy
- **CLAHE enhancement**: Adaptive histogram equalization for better feature detection

### 4. Temporal Visualization
- **Timeline slider**: Navigate through processed frames
- **Real-time statistics**: Average and maximum flow speeds
- **Time series plots**: Visualize speed changes over time
- **Velocity field heatmaps**: Color-coded speed visualizations

### 5. Data Export
- **CSV format**: For spreadsheet analysis
- **HDF5 format**: For scientific computing
- **JSON statistics**: Frame-by-frame speed statistics
- **Image sequences**: Velocity field visualizations

## Installation

### Prerequisites

```bash
# Python 3.8 or higher required
python --version

# Install required packages
pip install PyQt6 opencv-python numpy matplotlib vtk h5py
```

### Install OpyFlow

If you haven't installed the opyf package:

```bash
# From the opyflow directory
pip install -e .

# Or install from PyPI
pip install opyf
```

## Quick Start

### Launch the GUI

```bash
python flood_speed_gui.py
```

### Step-by-Step Workflow

#### Step 1: Load Video
1. Click **"Load Video (Drone/CCTV)"**
2. Select your video file
3. Video information will appear (frames, dimensions)

#### Step 2: Select Water Area
Choose one of two methods:

**Option A: Rectangle ROI**
1. Click **"Select Rectangle ROI"**
2. Draw a rectangle around the water area
3. Press ENTER to confirm, ESC to cancel

**Option B: Polygon Masking**
1. Click **"Draw Polygon Water Area"**
2. Click to add polygon points
3. Press ENTER when done, ESC to cancel
4. This masks out non-water objects (buildings, trees, etc.)

#### Step 3: Configure Processing Parameters

**Frame Range Settings:**
- **Start Frame**: First frame to analyze (default: 0)
- **Frame Step**: Number of frames between pair images (default: 1)
  - Larger values = larger displacements, but may lose tracking
- **Frame Shift**: Shift between consecutive pairs (default: 1)
- **Total Pairs**: Number of frame pairs to process

**Velocity Settings:**
- **Min Speed**: Minimum expected speed in pixels/frame
- **Max Speed**: Maximum expected speed in pixels/frame
  - Use these to filter unrealistic velocities

**Filter Settings:**
- **Filter Radius**: Spatial filter radius in pixels (default: 30)
  - Larger = smoother but less detail
- **Enable CLAHE**: Contrast enhancement (recommended: ON)
  - Helps in low-contrast or varying light conditions

#### Step 4: Process Video
1. Click **"Start Analysis"** (green button)
2. Monitor progress in the log window
3. Wait for processing to complete

#### Step 5: Explore Results

**Flow Vectors Tab:**
- Shows optical flow vectors overlaid on video frames

**Velocity Field Tab:**
- Color-coded heatmap of flow speeds
- Use the timeline slider to see different frames

**Time Series Tab:**
- Average speed over time (blue line)
- Maximum speed over time (red line)
- Standard deviation (shaded area)

**Timeline Control:**
- Drag the slider to navigate through results
- Speed statistics update in real-time

#### Step 6: Export Results
1. Click **"Export to CSV"** or **"Export to HDF5"**
2. Choose save location
3. Results include:
   - Velocity field data
   - Flow statistics (JSON file)

## Understanding the Parameters

### Time Vector Parameters

The processing plan is defined by four parameters:

```python
starting_frame = 0   # First frame to analyze
step = 1             # Frames between pair images
shift = 1            # Shift between pairs
Ntot = 10            # Number of pairs to process
```

**Example 1: Sequential pairs**
```
starting_frame=0, step=1, shift=1, Ntot=5
Processes: [0-1], [1-2], [2-3], [3-4], [4-5]
```

**Example 2: Larger displacement**
```
starting_frame=0, step=5, shift=1, Ntot=3
Processes: [0-5], [1-6], [2-7]
(Larger displacements, good for slow motion)
```

**Example 3: Non-overlapping**
```
starting_frame=0, step=1, shift=2, Ntot=3
Processes: [0-1], [2-3], [4-5]
(Faster processing, independent pairs)
```

### Velocity Limits (vlim)

Set realistic speed ranges to filter noise:

- **Slow flows** (calm water): `[0, 10]` px/frame
- **Moderate flows** (normal flood): `[0, 40]` px/frame
- **Fast flows** (rapid flood): `[0, 100]` px/frame

### Filter Parameters

**RadiusF**: Spatial neighborhood for outlier detection
- Small (10-20 px): Detailed but noisy
- Medium (30-50 px): Balanced
- Large (>50 px): Smooth but may miss details

**maxDevInRadius**: Maximum deviation tolerance
- Small (1-2): Strict filtering, removes more outliers
- Large (>5): Permissive filtering

**wayBackGoodFlag**: Bidirectional tracking threshold
- Ensures features can be tracked forward and backward
- Higher values = stricter (more reliable but fewer points)

## Programmatic Usage

For batch processing or automation, use the example script:

```python
from example_flood_analysis import analyze_flood_speed

analyzer, stats = analyze_flood_speed(
    video_path='/path/to/video.mp4',
    output_folder='./results'
)
```

## Tips for Best Results

### 1. Video Quality
- **Resolution**: Higher is better (720p minimum, 1080p+ recommended)
- **Frame rate**: 24-60 fps works well
- **Stability**: Stable camera gives better results
  - Use image stabilization if camera shakes
  - Drone footage: avoid windy conditions

### 2. Lighting Conditions
- **Consistent lighting**: Avoid rapid light changes
- **Enable CLAHE**: Helps with shadows and varying brightness
- **Avoid reflections**: Direct sun reflections can confuse tracking

### 3. Water Surface Features
- **Visible features**: Foam, debris, ripples help tracking
- **Avoid**: Completely smooth water (no features to track)
- **Good**: Turbulent water with visible surface patterns

### 4. Camera Angle
- **Nadir (top-down)**: Best for absolute velocity
- **Oblique**: Requires perspective correction
- **Use ROI**: Focus on water surface, exclude banks/obstacles

### 5. Processing Strategy
- **Start small**: Test with `Ntot=10` first
- **Check results**: Verify velocities are realistic
- **Adjust parameters**: Iterate to optimize
- **Full processing**: Run complete analysis once satisfied

## Output Files

### Velocity Field Data

**CSV Format:**
```
velocity_field_*.csv
├── Spatial coordinates (X, Y)
└── Velocity components (Ux, Uy)
```

**HDF5 Format:**
```
velocity_field.hdf5
├── /T_[s]          # Time vector
├── /X_[px]         # X coordinates
├── /Y_[px]         # Y coordinates
├── /Ux_[px.s-1]    # X velocity component
└── /Uy_[px.s-1]    # Y velocity component
```

### Statistics JSON

```json
[
  {
    "frame_index": 0,
    "avg_speed": 12.34,
    "max_speed": 45.67,
    "std_speed": 5.43
  },
  ...
]
```

## Scaling to Physical Units

To convert from pixels to real-world units (m/s):

```python
# After processing
analyzer.scaleData(
    framesPerSecond=30,        # Video FPS
    metersPerPx=0.05,          # Spatial scale (5 cm/pixel)
    unit=['m', 's'],           # Output units
    origin=[0, 0]              # Coordinate origin
)

# Re-export with physical units
analyzer.writeVelocityField(
    fileFormat='csv',
    outFolder='./results_scaled'
)
```

## Troubleshooting

### Issue: No features detected
**Solutions:**
- Enable CLAHE
- Lower `qualityLevel` in feature detection
- Increase contrast in video
- Check if ROI contains water surface

### Issue: Velocities too high/low
**Solutions:**
- Adjust `vlim` parameters
- Check `step` parameter (larger step = larger displacement)
- Verify video frame rate
- Check spatial scale

### Issue: Noisy velocity field
**Solutions:**
- Increase `RadiusF` (spatial filtering)
- Decrease `maxDevInRadius` (stricter filtering)
- Enable `wayBackGoodFlag` filtering
- Smooth temporal results in post-processing

### Issue: Processing is slow
**Solutions:**
- Reduce `Ntot` (process fewer frames)
- Increase `shift` (skip frames)
- Reduce ROI size
- Lower feature detection parameters

### Issue: GUI freezes
**Solutions:**
- Processing runs in background thread (should not freeze)
- Check log window for progress
- For very long videos, use programmatic processing
- Close other applications to free memory

## Advanced Features

### Custom Masking

Create complex masks programmatically:

```python
import cv2
import numpy as np

# Load first frame
frame = cv2.imread('first_frame.jpg', 0)

# Create mask
mask = np.zeros(frame.shape[:2], dtype=np.uint8)

# Define polygon points (water area)
water_polygon = np.array([[100, 200], [400, 150], [500, 400], [150, 450]])
cv2.fillPoly(mask, [water_polygon], 255)

# Apply to analyzer
analyzer.set_mask(mask)
```

### Bird's Eye View Transformation

For oblique camera angles:

```python
# Define ground control points
image_points = np.array([...])  # Points in image
model_points = np.array([...])  # Corresponding real-world coordinates

# Set bird's eye view
analyzer.set_birdEyeViewProcessing(
    image_points=image_points,
    model_points=model_points,
    pos_bird_cam=[0, 0, 10],  # Virtual camera position
    scale=True,
    framesPerSecond=30
)
```

### Hourly Analysis

For long-term monitoring:

```python
# Process video in hourly chunks
fps = 30  # frames per second
frames_per_hour = fps * 3600  # 108,000 frames

hourly_stats = []
for hour in range(24):
    start = hour * frames_per_hour

    analyzer.set_vecTime(
        starting_frame=start,
        step=fps,  # 1 second intervals
        shift=fps * 60,  # 1 minute shifts
        Ntot=60  # 60 measurements per hour
    )

    analyzer.extractGoodFeaturesPositionsDisplacementsAndInterpolate(
        display=False
    )

    # Calculate hourly average
    # ... process results ...
```

## References

- **OpyFlow Documentation**: [GitHub](https://github.com/groussea/opyflow)
- **Scientific Paper**: [Scanning PIV of turbulent flows](https://link.springer.com/article/10.1007/s00348-020-02990-y)
- **OpenCV Optical Flow**: [Lucas-Kanade Method](https://docs.opencv.org/master/d4/dee/tutorial_optical_flow.html)

## Citation

If you use this tool in your research, please cite:

```bibtex
@article{rousseau2020scanning,
  title={Scanning PIV of turbulent flows over and through rough porous beds using refractive index matching},
  author={Rousseau, Gauthier and Ancey, Christophe},
  journal={Experiments in Fluids},
  volume={61},
  number={8},
  pages={1--24},
  year={2020},
  publisher={Springer}
}
```

## Support

For issues or questions:
1. Check this documentation
2. Review the OpyFlow documentation
3. Open an issue on GitHub

## License

This tool is built on OpyFlow and follows the same license terms.

---

**Happy flood monitoring!** 🌊
