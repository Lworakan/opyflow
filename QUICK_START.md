# 🚀 Quick Start Guide - Flood Speed Analysis Tool

## ✅ You're Ready to Go!

The GUI has been successfully created and fixed for your environment.

## How to Launch

Simply run:

```bash
python flood_speed_gui.py
```

## 5-Minute Workflow

### 1. **Load Video** (30 seconds)
- Click "Load Video (Drone/CCTV)"
- Select your `.mp4`, `.avi`, or `.mov` file
- Video info appears on the left

### 2. **Select Water Area** (1 minute)
Choose ONE method:

**Method A: Draw Polygon (Recommended)**
- Click "Draw Polygon Water Area"
- Click points around the water area
- Press **ENTER** when done
- This masks out non-water objects

**Method B: Rectangle ROI**
- Click "Select Rectangle ROI"
- Drag to select area
- Press **ENTER**

### 3. **Start Analysis** (2-3 minutes)
- Click the green **"Start Analysis"** button
- Watch progress in the log window
- Processing time depends on:
  - Total Pairs (default: 10)
  - Video resolution
  - Computer speed

### 4. **Explore Results** (1 minute)
- **Velocity Field tab**: See speed heatmap
- **Time Series tab**: See speed over time
- Use the **timeline slider** to navigate
- Check speed statistics at the bottom

### 5. **Export** (30 seconds)
- Click "Export to CSV" or "Export to HDF5"
- Choose save location
- Done!

## Default Settings (Good for Most Cases)

The tool comes pre-configured with sensible defaults:

```
Start Frame: 0
Frame Step: 1
Total Pairs: 10
Min Speed: 0 px/frame
Max Speed: 50 px/frame
Filter Radius: 30 px
CLAHE: Enabled ✓
```

**For quick testing**, these settings work well!

## When to Adjust Settings

### Fast-Moving Water
```
Max Speed: 100+ px/frame
Frame Step: 2
```

### Slow-Moving Water
```
Max Speed: 20 px/frame
Frame Step: 1
```

### Noisy/Dark Video
```
CLAHE: ✓ (enabled)
Filter Radius: 40-50 px
```

### Long Video Analysis
```
Total Pairs: 100+
Frame Shift: 5-10 (skip frames)
```

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'opyf'"
```bash
pip install -e .
```

### ❌ GUI crashes or segfaults
Already fixed! Make sure you're using the updated `flood_speed_gui.py`

### ❌ No features detected
- Enable CLAHE checkbox
- Make sure water surface has visible patterns (foam, ripples, debris)
- Try lowering Max Speed limit

### ❌ Mask dimension error
Already fixed in the latest version!

## Understanding Your Results

### Speed Values
- Measured in **pixels/frame** by default
- To convert to m/s, you need to:
  1. Know video frame rate (e.g., 30 fps)
  2. Know spatial scale (e.g., 0.05 m/pixel)
  3. Use: `speed_m/s = speed_px/frame × fps × m/px`

### Visualizations
- **Blue in heatmap**: Slow flow
- **Red in heatmap**: Fast flow
- **White/NaN**: No data or masked area

### Statistics
- **Avg Speed**: Average flow in the water area
- **Max Speed**: Highest velocity detected
- **Std Dev** (in Time Series): Flow variability

## Example Videos

Your tool works great with:
- ✅ Drone footage (nadir/top-down view)
- ✅ CCTV cameras (fixed position)
- ✅ Phone videos (if stable)
- ✅ Action camera footage

Best quality:
- 1080p or higher resolution
- 30+ fps
- Stable camera
- Good lighting
- Visible water surface features

## Next Steps

### Learn More
- Full guide: `FLOOD_SPEED_GUI_README.md`
- Technical details: `FLOOD_SPEED_TOOL_SUMMARY.md`
- Installation help: `INSTALLATION_GUIDE.md`

### Programmatic Usage
For batch processing, check out:
```bash
python example_flood_analysis.py
```

Edit the `video_path` variable to point to your video.

## What You Can Do

✅ Analyze flood speeds from any video
✅ Track speed changes over time
✅ Focus on specific water areas
✅ Ignore buildings, banks, trees
✅ Export data for further analysis
✅ Create publication-quality plots
✅ Process multiple videos in batch
✅ Integrate into your workflow

## Tips for Success

1. **Start Small**: Process 10-20 frame pairs first to test settings
2. **Use Masking**: Draw polygon to exclude non-water areas
3. **Check Results**: Verify speeds are realistic before long processing
4. **Export Often**: Save results as you go
5. **Read Docs**: Check the full guide for advanced features

## Common Workflows

### Quick Assessment
```
Total Pairs: 10
→ Fast preview of flood speeds
```

### Detailed Analysis
```
Total Pairs: 100+
Frame Shift: 1
→ Complete temporal evolution
```

### Hourly Monitoring
```
Step: 30 (if 30 fps video = 1 second)
Shift: 1800 (= 1 minute)
Total Pairs: 60 (= 1 hour)
→ One measurement per minute for one hour
```

## Getting Help

1. Check log window for error messages
2. Read `FLOOD_SPEED_GUI_README.md`
3. Try example script: `example_flood_analysis.py`
4. Check OpyFlow docs: https://github.com/groussea/opyflow

## You're All Set! 🎉

The tool is ready to use. Just run:

```bash
python flood_speed_gui.py
```

Load a video, select the water area, and start analyzing!

---

**Happy flood monitoring!** 🌊📊
