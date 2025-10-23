# Flood Polygon Analyzer - Usage Guide

## Command Line Arguments

The script now supports command-line arguments for flexible video input and configuration.

### Basic Usage

```bash
# Use default video
python flood_polygon_analyzer.py

# Specify a custom video
python flood_polygon_analyzer.py --video /path/to/your/flood_video.mp4

# Short form
python flood_polygon_analyzer.py -v /path/to/your/flood_video.mp4
```

### Advanced Options

```bash
# Specify video and background frame
python flood_polygon_analyzer.py --video video.mp4 --frame 30

# With scaling parameters
python flood_polygon_analyzer.py -v video.mp4 --fps 30 --scale 0.02

# Full example with all options
python flood_polygon_analyzer.py \
  --video /path/to/flood.mp4 \
  --frame 25 \
  --fps 25 \
  --scale 0.015
```

### Command Line Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--video` | `-v` | string | canuelas.mp4 | Path to input video file |
| `--frame` | `-f` | int | 20 | Frame number for static background |
| `--fps` | | float | None | Frames per second (for time scaling) |
| `--scale` | | float | None | Meters per pixel (for spatial scaling) |
| `--help` | `-h` | | | Show help message and exit |

### Examples

#### 1. Analyze a specific flood video

```bash
python flood_polygon_analyzer.py --video /Users/worakanlasudee/Documents/flood_event_2024.mp4
```

#### 2. Use frame 50 as background

```bash
python flood_polygon_analyzer.py -v flood.mp4 --frame 50
```

#### 3. With real-world scaling

```bash
# 30 fps video, 2cm per pixel
python flood_polygon_analyzer.py \
  -v flood.mp4 \
  --fps 30 \
  --scale 0.02
```

#### 4. Get help

```bash
python flood_polygon_analyzer.py --help
```

Output:
```
usage: flood_polygon_analyzer.py [-h] [-v VIDEO] [-f FRAME] [--fps FPS] [--scale SCALE]

Interactive Flood Area Analyzer with Speed Visualization

optional arguments:
  -h, --help            show this help message and exit
  -v VIDEO, --video VIDEO
                        Path to the input video file (MP4, AVI, etc.)
  -f FRAME, --frame FRAME
                        Frame number to use as static background (default: 20)
  --fps FPS             Frames per second for time scaling (optional)
  --scale SCALE         Meters per pixel for spatial scaling (optional)

Examples:
  python flood_polygon_analyzer.py --video /path/to/flood_video.mp4
  python flood_polygon_analyzer.py -v /path/to/flood_video.mp4 --frame 30
  python flood_polygon_analyzer.py --help
```

## Workflow

### 1. Launch with your video

```bash
python flood_polygon_analyzer.py -v my_flood_video.mp4
```

### 2. Draw regions of interest

- Select **Polygon** or **Circle** mode
- Draw shapes around flood areas
- Right-click to close polygons

### 3. Analyze flow

- **Analyze Flow**: See velocity vectors inside shapes only
- **Show Fastest**: Highlight fastest flood areas
- **Speed vs Time**: Plot temporal evolution

### 4. Export results

- **Save**: Save shapes to reload later
- **Export**: Generate CSV/HDF5/JSON files

## Tips

### Choosing the Right Background Frame

The `--frame` parameter selects which frame to display as the static background:

- **Early frames (0-10)**: Use if flood hasn't started yet
- **Mid frames (15-30)**: Good for most videos, shows partial flood
- **Later frames (30+)**: Use if you want to see peak flood conditions

Try different values to find the clearest view of your flood area.

### Scaling Your Data

Use `--fps` and `--scale` to convert from pixels/frame to real units:

```bash
# If your video is 25 fps and each pixel = 0.015 meters
python flood_polygon_analyzer.py -v video.mp4 --fps 25 --scale 0.015

# Output will be in m/s instead of px/frame
```

### Error: Video file not found

If you see:
```
ERROR: Video file not found: /path/to/video.mp4
```

Solutions:
1. Check the path is correct
2. Use absolute path instead of relative
3. Verify file exists: `ls -la /path/to/video.mp4`

### Error: Could not load frame

If you see:
```
ERROR: Could not load frame 50 from video
```

The video might be shorter than expected. Try:
```bash
# Use an earlier frame
python flood_polygon_analyzer.py -v video.mp4 --frame 10
```

## File Outputs

When you export, these files are created:

1. **flood_shapes.json** - Saved polygons/circles
2. **shape_flow_statistics.json** - Velocity stats for each shape
3. **flow_speed_over_time.csv** - Temporal data (if you used Speed vs Time)
4. **frame_X_to_Y.csv** - Full velocity field
5. **frame_X_to_Y.hdf5** - Velocity field (compressed)

## Quick Reference

```bash
# Most common usage patterns:

# 1. Quick analysis with default settings
python flood_polygon_analyzer.py -v my_video.mp4

# 2. Choose background frame
python flood_polygon_analyzer.py -v my_video.mp4 -f 25

# 3. Real-world units
python flood_polygon_analyzer.py -v my_video.mp4 --fps 30 --scale 0.02

# 4. See all options
python flood_polygon_analyzer.py --help
```
