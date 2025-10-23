# Flood Speed GUI - Visualization Guide

## Updated Visualization Features

The GUI now displays velocity fields **overlaid on actual video frames**, just like professional PIV software!

## What You'll See

### Velocity Field Tab
The visualization shows:
- **Background**: Actual video frame from your footage
- **Overlay**: Semi-transparent colored velocity field
  - 🟦 Blue = Slow flow
  - 🟨 Yellow = Medium flow
  - 🟥 Red = Fast flow
- **Grid**: White gridlines for spatial reference
- **Colorbar**: Shows velocity scale (px/frame or m/s)

This matches the style of `/tests/Test_Navizence/gif/frame_final_3.png`

## How to Use

### 1. Process Your Video
```
Load video → Select area → Start Analysis
```

### 2. Navigate Through Results
- Use the **timeline slider** at the bottom
- Each position shows velocity field for different frame pair
- **Speed statistics** update in real-time

### 3. Save Individual Frames
**NEW FEATURE:** Click **"Save Current Frame"** button
- Saves the current visualization as high-quality PNG
- Use slider to select which frame to save
- Perfect for reports, presentations, papers

### 4. Export All Data
- **Export to CSV**: Velocity data in spreadsheet format
- **Export to HDF5**: Scientific computing format
- **Statistics JSON**: Frame-by-frame speed data

## Visualization Details

### What's Displayed

```
┌─────────────────────────────────────┐
│  Video Frame (Background)           │
│  ┌─────────────────────────────┐   │
│  │  🟦🟨🟥 Velocity Overlay     │   │
│  │  (Semi-transparent)          │   │
│  │                               │   │
│  │  Grid lines for reference    │   │
│  └─────────────────────────────┘   │
│                                     │
│  Colorbar: Speed scale              │
└─────────────────────────────────────┘
```

### Parameters

- **Alpha (transparency)**: 0.6 (configurable in code)
- **Colormap**: 'jet' (blue → yellow → red)
- **Interpolation**: Bilinear (smooth)
- **Grid**: White, 30% transparent

## Customizing Visualizations

### Change Colormap
Edit line ~591 in `flood_speed_gui.py`:
```python
cmap='jet'  # Try: 'viridis', 'plasma', 'coolwarm', 'RdYlBu'
```

### Adjust Transparency
Edit line ~593:
```python
alpha=0.6  # Range: 0.0 (invisible) to 1.0 (opaque)
```

### Change Grid Style
Edit line ~604:
```python
self.field_canvas.axes.grid(True, color='white', alpha=0.3, linewidth=0.5)
# Try: color='black', alpha=0.5, linewidth=1.0
```

### Higher Resolution Exports
Edit line ~719:
```python
dpi=150  # Try: 300 for publication quality
```

## Example Workflow

### Quick Assessment
```
1. Load video
2. Process 10 frames
3. Use slider to check all frames
4. Save interesting frames
```

### Complete Analysis
```
1. Load video
2. Process 100+ frames
3. Navigate with slider
4. Save key frames showing:
   - Peak flood speed
   - Flow pattern changes
   - Different flood stages
5. Export all data for further analysis
```

### Presentation Prep
```
1. Process your video
2. Find 3-5 representative frames:
   - Beginning (slow flow)
   - Peak (fast flow)
   - End (receding)
3. Save each with "Save Current Frame"
4. Use in PowerPoint/reports
```

## Visualization Tips

### For Clear Images
- ✓ High contrast videos work best
- ✓ Good lighting helps
- ✓ Use CLAHE for low-contrast videos
- ✓ Mask non-water areas

### For Publications
- ✓ Save at high DPI (300)
- ✓ Add scale bar in post-processing
- ✓ Include units in labels
- ✓ Use appropriate colormap

### For Presentations
- ✓ DPI 150 is usually sufficient
- ✓ Choose contrasting colormaps
- ✓ Save multiple time points
- ✓ Show flow evolution

## Output Files

### Frame Visualizations (PNG)
```
frame_0_velocity_field.png
frame_10_velocity_field.png
frame_20_velocity_field.png
...
```

Each shows:
- Video background
- Velocity overlay
- Grid
- Colorbar with units
- Title with frame number

### Data Exports
- **CSV**: Velocity components (Ux, Uy) at grid points
- **HDF5**: Complete velocity field time series
- **JSON**: Statistical summary (avg, max, std)

## Comparison with Other Tools

| Feature | This GUI | PIVlab | DaVis | Commercial |
|---------|----------|--------|-------|------------|
| Video overlay | ✓ | ✓ | ✓ | ✓ |
| Real-time slider | ✓ | Limited | ✓ | ✓ |
| One-click save | ✓ | Manual | ✓ | ✓ |
| Customizable | ✓ | Limited | ✓ | ✓ |
| Free | ✓ | ✓ | ✗ | ✗ |

## Advanced Customization

### Add Quiver Plot
Want to see flow arrows? Add this after line 601:
```python
# Downsample for quiver plot
step = 10
X, Y = np.meshgrid(
    range(0, ux.shape[1], step),
    range(0, ux.shape[0], step)
)
U = ux[::step, ::step]
V = uy[::step, ::step]

self.field_canvas.axes.quiver(
    X, Y, U, V,
    color='white',
    alpha=0.7,
    scale=50,
    width=0.003
)
```

### Add Streamlines
For flow patterns, add after velocity field:
```python
self.field_canvas.axes.streamplot(
    range(ux.shape[1]),
    range(ux.shape[0]),
    ux, uy,
    color='white',
    linewidth=1,
    density=1.5,
    arrowsize=1.5
)
```

### Add Scale Bar
For physical scale:
```python
from matplotlib_scalebar.scalebar import ScaleBar
scalebar = ScaleBar(0.05, "m", length_fraction=0.25)
self.field_canvas.axes.add_artist(scalebar)
```

## Troubleshooting

### Colorbar overlaps plot
The GUI automatically removes old colorbars. If issues persist:
```python
# Line ~612-614 handles this
if hasattr(self, '_colorbar') and self._colorbar is not None:
    self._colorbar.remove()
```

### Background frame not showing
Check that video frames are loading:
```python
# Line ~570-572
frame_idx = self.processing_results.vec[index * 2]
self.processing_results.readFrame(frame_idx)
```

### Overlay too dark/light
Adjust alpha value (line ~593):
```python
alpha=0.4  # Lighter overlay
alpha=0.8  # Darker overlay
```

## Examples

### Saved Frame Names
```
flood_peak_frame_45.png
slow_flow_frame_10.png
receding_frame_90.png
```

### Folder Organization
```
my_analysis/
├── raw_data/
│   ├── flood_velocity_field.csv
│   └── flood_velocity_field.hdf5
├── statistics/
│   └── flood_velocity_field_statistics.json
└── visualizations/
    ├── frame_0_velocity_field.png
    ├── frame_10_velocity_field.png
    └── frame_20_velocity_field.png
```

## Quick Reference

| Task | Action |
|------|--------|
| Change frame | Move timeline slider |
| Save current | Click "Save Current Frame" |
| Export all | Click "Export to CSV/HDF5" |
| Change speed range | Adjust Min/Max Speed before processing |
| Reprocess | Load new parameters, click "Start Analysis" |

## Color Scale Reference

### Jet Colormap (Default)
```
0% ────── Blue (Slow)
25% ───── Cyan
50% ───── Yellow (Medium)
75% ───── Orange
100% ──── Red (Fast)
```

### Alternative Colormaps
- **viridis**: Purple → Green → Yellow
- **plasma**: Purple → Pink → Yellow
- **coolwarm**: Blue → White → Red
- **RdYlBu**: Red → Yellow → Blue

## Integration

### With Reports
1. Save multiple frames
2. Insert into Word/LaTeX
3. Add captions with context
4. Reference frame numbers

### With GIS
1. Export velocity data (CSV)
2. Georeference in QGIS/ArcGIS
3. Overlay on maps
4. Create spatial analysis

### With Python
1. Export HDF5 data
2. Load in Python/MATLAB
3. Further processing
4. Custom visualizations

---

**The GUI now creates professional-quality visualizations automatically!**

Just process your video and use the slider to explore results. 🌊📊
