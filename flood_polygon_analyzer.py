
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Flood Area Polygon Drawing Tool
Based on test_opyf_Navizence.py with polygon drawing capabilities

Created: 2025
@author: Modified for flood area analysis
"""

import sys
import opyf
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import matplotlib
from matplotlib.patches import Polygon, Circle
from matplotlib.widgets import Button
from matplotlib.widgets import RadioButtons
import json
import argparse

matplotlib.use('TkAgg')
plt.ion()
plt.close('all')

class FloodPolygonAnalyzer:
    """
    Interactive flood area analyzer with polygon and circle drawing capabilities
    Includes automatic visualization of fastest flood speed areas
    """

    def __init__(self, video_path):
        """Initialize the analyzer with video path"""
        self.video_path = video_path
        self.video = opyf.videoAnalyzer(video_path)

        # Polygon drawing state
        self.polygons = []  # List to store multiple polygons
        self.current_polygon = []  # Points of the current polygon being drawn
        self.drawing = False
        self.polygon_patches = []

        # Circle drawing state
        self.circles = []  # List to store circles (center_x, center_y, radius)
        self.circle_patches = []
        self.circle_center = None
        self.temp_circle = None

        # Drawing mode
        self.draw_mode = 'polygon'  # 'polygon' or 'circle'

        # Speed visualization
        self.speed_circles = []  # Circles highlighting fastest areas

        # Figure and axes references
        self.fig = None
        self.ax = None
        self.background_image = None

        # Store the first frame for static background
        self.static_frame = None

        # Scaling parameters
        self.apply_scaling = False
        self.scale_fps = 25
        self.scale_meters_per_px = 1.0

    def load_static_frame(self, frame_index=0):
        """Load and store a static frame for polygon drawing"""
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        cap.release()

        if ret:
            # Convert BGR to RGB
            self.static_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return True
        return False

    def setup_interactive_plot(self):
        """Setup the interactive matplotlib figure for polygon/circle drawing"""
        self.fig, self.ax = plt.subplots(figsize=(14, 9))
        plt.subplots_adjust(bottom=0.15, left=0.15)

        if self.static_frame is not None:
            self.background_image = self.ax.imshow(self.static_frame)
            self.update_title()
        else:
            self.ax.set_title('No frame loaded')

        # Add mode selector (radio buttons)
        ax_radio = plt.axes([0.02, 0.7, 0.1, 0.15])
        self.radio = RadioButtons(ax_radio, ('Polygon', 'Circle'))
        self.radio.on_clicked(self.set_draw_mode)

        # Add control buttons (Row 1)
        ax_clear = plt.axes([0.15, 0.08, 0.08, 0.04])
        ax_save = plt.axes([0.24, 0.08, 0.08, 0.04])
        ax_load = plt.axes([0.33, 0.08, 0.08, 0.04])
        ax_analyze = plt.axes([0.42, 0.08, 0.1, 0.04])
        ax_show_fast = plt.axes([0.53, 0.08, 0.12, 0.04])
        ax_clear_viz = plt.axes([0.66, 0.08, 0.1, 0.04])
        ax_export = plt.axes([0.77, 0.08, 0.08, 0.04])

        # Add control buttons (Row 2)
        ax_time_plot = plt.axes([0.15, 0.02, 0.15, 0.04])
        ax_export_video = plt.axes([0.31, 0.02, 0.15, 0.04])

        self.btn_clear = Button(ax_clear, 'Clear Last')
        self.btn_save = Button(ax_save, 'Save')
        self.btn_load = Button(ax_load, 'Load')
        self.btn_analyze = Button(ax_analyze, 'Analyze Flow')
        self.btn_show_fast = Button(ax_show_fast, 'Show Fastest')
        self.btn_clear_viz = Button(ax_clear_viz, 'Clear Viz')
        self.btn_export = Button(ax_export, 'Export')
        self.btn_time_plot = Button(ax_time_plot, 'Speed vs Time')
        self.btn_export_video = Button(ax_export_video, 'Export Video')

        # Connect button events
        self.btn_clear.on_clicked(self.clear_last_shape)
        self.btn_save.on_clicked(self.save_shapes)
        self.btn_load.on_clicked(self.load_shapes)
        self.btn_analyze.on_clicked(self.analyze_flow_in_shapes)
        self.btn_show_fast.on_clicked(self.visualize_fastest_areas)
        self.btn_clear_viz.on_clicked(self.clear_speed_visualization)
        self.btn_export.on_clicked(self.export_results)
        self.btn_time_plot.on_clicked(self.plot_flow_speed_over_time)
        self.btn_export_video.on_clicked(self.export_video_with_flow)

        # Connect mouse events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        plt.show()

    def update_title(self):
        """Update the title based on current drawing mode"""
        if self.draw_mode == 'polygon':
            self.ax.set_title('POLYGON MODE: Left-click to add points | Right-click to close polygon')
        else:
            self.ax.set_title('CIRCLE MODE: Left-click for center | Drag to set radius')

    def set_draw_mode(self, label):
        """Change drawing mode between polygon and circle"""
        self.draw_mode = label.lower()
        self.current_polygon = []  # Clear any partial polygon
        self.circle_center = None
        if self.temp_circle:
            self.temp_circle.remove()
            self.temp_circle = None
        self.update_title()
        self.fig.canvas.draw()

    def on_click(self, event):
        """Handle mouse click events for polygon/circle drawing"""
        if event.inaxes != self.ax:
            return

        if self.draw_mode == 'polygon':
            # Left click - add point to polygon
            if event.button == 1:
                self.current_polygon.append([event.xdata, event.ydata])
                self.ax.plot(event.xdata, event.ydata, 'ro', markersize=5)

                # Draw line segments
                if len(self.current_polygon) > 1:
                    p1 = self.current_polygon[-2]
                    p2 = self.current_polygon[-1]
                    self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', linewidth=2)

                self.fig.canvas.draw()

            # Right click - close polygon
            elif event.button == 3:
                if len(self.current_polygon) >= 3:
                    # Close the polygon
                    polygon = Polygon(self.current_polygon,
                                    fill=True,
                                    alpha=0.3,
                                    facecolor='red',
                                    edgecolor='yellow',
                                    linewidth=2)
                    self.ax.add_patch(polygon)
                    self.polygon_patches.append(polygon)
                    self.polygons.append(np.array(self.current_polygon))

                    print(f"✓ Polygon {len(self.polygons)} created with {len(self.current_polygon)} points")
                    print(f"  Total polygons stored: {len(self.polygons)}")
                    self.current_polygon = []
                    self.fig.canvas.draw()
                else:
                    print("⚠ Need at least 3 points to create a polygon (currently {len(self.current_polygon)} points)")

        elif self.draw_mode == 'circle':
            # Left click - set circle center
            if event.button == 1:
                self.circle_center = (event.xdata, event.ydata)
                # Draw center marker
                self.ax.plot(event.xdata, event.ydata, 'go', markersize=8)
                self.fig.canvas.draw()
                print(f"Circle center set at ({event.xdata:.1f}, {event.ydata:.1f})")

    def on_release(self, event):
        """Handle mouse release events for circle drawing"""
        if event.inaxes != self.ax:
            return

        if self.draw_mode == 'circle' and self.circle_center is not None:
            # Calculate radius
            dx = event.xdata - self.circle_center[0]
            dy = event.ydata - self.circle_center[1]
            radius = np.sqrt(dx**2 + dy**2)

            if radius > 5:  # Minimum radius threshold
                # Create circle
                circle = Circle(self.circle_center, radius,
                              fill=True,
                              alpha=0.3,
                              facecolor='blue',
                              edgecolor='cyan',
                              linewidth=2)
                self.ax.add_patch(circle)
                self.circle_patches.append(circle)
                self.circles.append({
                    'center': self.circle_center,
                    'radius': radius
                })

                print(f"Circle {len(self.circles)} created: center=({self.circle_center[0]:.1f}, {self.circle_center[1]:.1f}), radius={radius:.1f}")

            # Clean up
            self.circle_center = None
            if self.temp_circle:
                self.temp_circle.remove()
                self.temp_circle = None
            self.fig.canvas.draw()

    def on_motion(self, event):
        """Show preview for circle drawing"""
        if event.inaxes != self.ax:
            return

        if self.draw_mode == 'circle' and self.circle_center is not None:
            # Show preview circle
            dx = event.xdata - self.circle_center[0]
            dy = event.ydata - self.circle_center[1]
            radius = np.sqrt(dx**2 + dy**2)

            if self.temp_circle:
                self.temp_circle.remove()

            self.temp_circle = Circle(self.circle_center, radius,
                                    fill=False,
                                    edgecolor='green',
                                    linewidth=1,
                                    linestyle='--')
            self.ax.add_patch(self.temp_circle)
            self.fig.canvas.draw()

    def clear_last_shape(self, event=None):
        """Remove the last drawn shape (polygon or circle)"""
        # Try to remove last circle first
        if len(self.circles) > 0:
            self.circles.pop()
            patch = self.circle_patches.pop()
            patch.remove()
            self.fig.canvas.draw()
            print(f"Removed last circle. {len(self.circles)} circles remaining")
        # Otherwise remove last polygon
        elif len(self.polygons) > 0:
            self.polygons.pop()
            patch = self.polygon_patches.pop()
            patch.remove()
            self.fig.canvas.draw()
            print(f"Removed last polygon. {len(self.polygons)} polygons remaining")
        else:
            print("No shapes to remove")

    def save_shapes(self, event=None):
        """Save both polygons and circles to JSON file"""
        # Debug output
        print(f"DEBUG: Number of polygons = {len(self.polygons)}")
        print(f"DEBUG: Number of circles = {len(self.circles)}")
        print(f"DEBUG: self.polygons = {self.polygons}")
        print(f"DEBUG: self.circles = {self.circles}")

        if len(self.polygons) == 0 and len(self.circles) == 0:
            print("No shapes to save")
            print("Make sure to:")
            print("  1. Draw at least 3 points for a polygon")
            print("  2. RIGHT-CLICK to close the polygon")
            print("  3. For circles, click and drag then release")
            return

        data = {
            'video_path': self.video_path,
            'polygons': [poly.tolist() for poly in self.polygons],
            'circles': [{'center': list(c['center']), 'radius': float(c['radius'])}
                       for c in self.circles]
        }

        filename = 'flood_shapes.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Saved {len(self.polygons)} polygon(s) and {len(self.circles)} circle(s) to {filename}")

    def load_shapes(self, event=None):
        """Load polygons and circles from JSON file"""
        filename = 'flood_shapes.json'
        if not os.path.exists(filename):
            print(f"{filename} not found")
            return

        with open(filename, 'r') as f:
            data = json.load(f)

        # Clear existing shapes
        for patch in self.polygon_patches:
            patch.remove()
        for patch in self.circle_patches:
            patch.remove()
        self.polygons = []
        self.polygon_patches = []
        self.circles = []
        self.circle_patches = []

        # Load polygons
        if 'polygons' in data:
            for poly_data in data['polygons']:
                poly_array = np.array(poly_data)
                self.polygons.append(poly_array)

                polygon = Polygon(poly_array,
                                fill=True,
                                alpha=0.3,
                                facecolor='red',
                                edgecolor='yellow',
                                linewidth=2)
                self.ax.add_patch(polygon)
                self.polygon_patches.append(polygon)

        # Load circles
        if 'circles' in data:
            for circ_data in data['circles']:
                center = tuple(circ_data['center'])
                radius = circ_data['radius']
                self.circles.append({'center': center, 'radius': radius})

                circle = Circle(center, radius,
                              fill=True,
                              alpha=0.3,
                              facecolor='blue',
                              edgecolor='cyan',
                              linewidth=2)
                self.ax.add_patch(circle)
                self.circle_patches.append(circle)

        self.fig.canvas.draw()
        print(f"Loaded {len(self.polygons)} polygon(s) and {len(self.circles)} circle(s) from {filename}")

    def point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using ray casting"""
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def point_in_circle(self, point, circle):
        """Check if a point is inside a circle"""
        x, y = point
        cx, cy = circle['center']
        radius = circle['radius']
        distance = np.sqrt((x - cx)**2 + (y - cy)**2)
        return distance <= radius

    def analyze_flow_in_shapes(self, event=None):
        """Analyze optical flow within defined shapes (polygons and circles)"""
        if len(self.polygons) == 0 and len(self.circles) == 0:
            print("No shapes defined. Please draw shapes first.")
            return

        print("\n" + "="*50)
        print("ANALYZING FLOW IN SHAPES ONLY")
        print("="*50)

        # Get processing parameters
        start_frame = getattr(self, 'processing_start_frame', 20)
        step = getattr(self, 'processing_step', 2)
        # Use user-specified Ntot, or default to 10 for quick analysis
        Ntot = getattr(self, 'processing_Ntot', 10)

        print(f"Flow analysis: starting_frame={start_frame}, step={step}, Ntot={Ntot}")

        # Configure video analysis
        self.video.set_vecTime(starting_frame=start_frame, step=step, shift=1, Ntot=Ntot)
        self.video.set_vlim([0, 30])
        self.video.set_filtersParams(wayBackGoodFlag=4, RadiusF=20,
                                    maxDevInRadius=1, CLAHE=True)
        self.video.set_goodFeaturesToTrackParams(maxCorners=50000, qualityLevel=0.001)
        self.video.set_opticalFlowParams(maxLevel=3)

        # Extract flow field WITHOUT automatic display
        print("Extracting velocity field in polygon areas only...")
        self.video.extractGoodFeaturesDisplacementsAccumulateAndInterpolate(
            display1=None, display2=None)  # Don't display all vectors

        # Create new figure for filtered visualization
        fig_flow, ax_flow = plt.subplots(figsize=(12, 8))
        ax_flow.imshow(self.static_frame)
        ax_flow.set_title('Velocity Vectors - Inside Polygons/Circles Only')

        # Filter and display vectors only inside shapes
        if hasattr(self.video, 'X') and hasattr(self.video, 'V'):
            # Handle different possible structures of X and V
            if isinstance(self.video.X, list) and len(self.video.X) > 0:
                X_data = self.video.X[0]
                V_data = self.video.V[0]
            else:
                X_data = self.video.X
                V_data = self.video.V

            filtered_x = []
            filtered_y = []
            filtered_vx = []
            filtered_vy = []
            filtered_magnitude = []

            total_points = len(X_data)
            points_inside = 0

            # Iterate through position and velocity data
            for j in range(len(X_data)):
                try:
                    # Try different indexing methods
                    if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                        x, y = X_data[j][0], X_data[j][1]
                    else:
                        # X_data might be structured as separate arrays
                        x = X_data[j]
                        y = X_data[j] if isinstance(X_data[j], (int, float)) else X_data[j]
                        continue  # Skip if structure is unclear

                    inside_any_shape = False

                    # Check if point is in any polygon
                    for polygon in self.polygons:
                        if self.point_in_polygon([x, y], polygon):
                            inside_any_shape = True
                            break

                    # Check if point is in any circle
                    if not inside_any_shape:
                        for circle in self.circles:
                            if self.point_in_circle([x, y], circle):
                                inside_any_shape = True
                                break

                    # Only keep vectors inside shapes
                    if inside_any_shape:
                        if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                            vx = V_data[j][0]
                            vy = V_data[j][1]
                        else:
                            continue

                        magnitude = np.sqrt(vx**2 + vy**2)

                        filtered_x.append(x)
                        filtered_y.append(y)
                        filtered_vx.append(vx)
                        filtered_vy.append(vy)
                        filtered_magnitude.append(magnitude)
                        points_inside += 1
                except (IndexError, TypeError) as e:
                    continue  # Skip problematic data points

            print(f"\nFiltered {points_inside}/{total_points} velocity vectors inside shapes")

            # Display filtered vectors as quiver plot
            if len(filtered_x) > 0:
                # Color by magnitude
                filtered_magnitude = np.array(filtered_magnitude)
                quiver = ax_flow.quiver(filtered_x, filtered_y, filtered_vx, filtered_vy,
                                       filtered_magnitude,
                                       cmap='jet', scale=200, width=0.003,
                                       headwidth=4, headlength=5)
                plt.colorbar(quiver, ax=ax_flow, label='Velocity (px/frame)')

                # Overlay the polygon/circle boundaries
                for polygon in self.polygons:
                    poly_patch = Polygon(polygon, fill=False,
                                        edgecolor='yellow', linewidth=2)
                    ax_flow.add_patch(poly_patch)

                for circle in self.circles:
                    circle_patch = Circle(circle['center'], circle['radius'],
                                         fill=False, edgecolor='cyan', linewidth=2)
                    ax_flow.add_patch(circle_patch)

                plt.tight_layout()
                plt.show()
            else:
                print("No velocity vectors found inside the drawn shapes!")
                plt.close(fig_flow)

        # Analyze each polygon - use the same X_data/V_data from above
        for i, polygon in enumerate(self.polygons):
            print(f"\nPolygon {i+1}:")
            print(f"  Number of vertices: {len(polygon)}")

            # Get velocity data
            if hasattr(self.video, 'X') and hasattr(self.video, 'V'):
                velocities_in_polygon = []

                for j in range(len(X_data)):
                    try:
                        if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                            x, y = X_data[j][0], X_data[j][1]
                        else:
                            continue

                        if self.point_in_polygon([x, y], polygon):
                            if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                                vx = V_data[j][0]
                                vy = V_data[j][1]
                                magnitude = np.sqrt(vx**2 + vy**2)
                                velocities_in_polygon.append(magnitude)
                    except (IndexError, TypeError):
                        continue

                if len(velocities_in_polygon) > 0:
                    print(f"  Points inside: {len(velocities_in_polygon)}")
                    print(f"  Mean velocity: {np.mean(velocities_in_polygon):.2f} px/frame")
                    print(f"  Max velocity: {np.max(velocities_in_polygon):.2f} px/frame")
                    print(f"  Min velocity: {np.min(velocities_in_polygon):.2f} px/frame")
                    print(f"  Std velocity: {np.std(velocities_in_polygon):.2f} px/frame")
                else:
                    print("  No velocity points found in this polygon")

            # Calculate polygon area
            area = self.calculate_polygon_area(polygon)
            print(f"  Polygon area: {area:.2f} px²")

        # Analyze each circle
        for i, circle in enumerate(self.circles):
            print(f"\nCircle {i+1}:")
            print(f"  Center: ({circle['center'][0]:.1f}, {circle['center'][1]:.1f})")
            print(f"  Radius: {circle['radius']:.1f} px")

            # Get velocity data
            if hasattr(self.video, 'X') and hasattr(self.video, 'V'):
                velocities_in_circle = []

                for j in range(len(X_data)):
                    try:
                        if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                            x, y = X_data[j][0], X_data[j][1]
                        else:
                            continue

                        if self.point_in_circle([x, y], circle):
                            if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                                vx = V_data[j][0]
                                vy = V_data[j][1]
                                magnitude = np.sqrt(vx**2 + vy**2)
                                velocities_in_circle.append(magnitude)
                    except (IndexError, TypeError):
                        continue

                if len(velocities_in_circle) > 0:
                    print(f"  Points inside: {len(velocities_in_circle)}")
                    print(f"  Mean velocity: {np.mean(velocities_in_circle):.2f} px/frame")
                    print(f"  Max velocity: {np.max(velocities_in_circle):.2f} px/frame")
                    print(f"  Min velocity: {np.min(velocities_in_circle):.2f} px/frame")
                    print(f"  Std velocity: {np.std(velocities_in_circle):.2f} px/frame")
                else:
                    print("  No velocity points found in this circle")

            # Calculate circle area
            area = np.pi * circle['radius']**2
            print(f"  Circle area: {area:.2f} px²")

        print("\n" + "="*50)

    def calculate_polygon_area(self, polygon):
        """Calculate polygon area using shoelace formula"""
        x = polygon[:, 0]
        y = polygon[:, 1]
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    def visualize_fastest_areas(self, event=None):
        """
        Automatically identify and visualize areas with the fastest flood speed
        using circles to highlight high-velocity regions (only within drawn shapes)
        """
        print("\n" + "="*50)
        print("FINDING FASTEST FLOOD SPEED AREAS IN POLYGONS")
        print("="*50)

        # Check if shapes are drawn
        if len(self.polygons) == 0 and len(self.circles) == 0:
            print("⚠ No shapes defined. Draw polygons/circles first to define flood areas!")
            return

        # Run flow analysis if not done yet
        if not hasattr(self.video, 'X') or len(self.video.X) == 0:
            print("Running flow analysis first...")
            # Get processing parameters
            start_frame = getattr(self, 'processing_start_frame', 20)
            step = getattr(self, 'processing_step', 2)
            Ntot = getattr(self, 'processing_Ntot', 10)

            print(f"  Using: starting_frame={start_frame}, step={step}, Ntot={Ntot}")
            self.video.set_vecTime(starting_frame=start_frame, step=step, shift=1, Ntot=Ntot)
            self.video.set_vlim([0, 30])
            self.video.set_filtersParams(wayBackGoodFlag=4, RadiusF=20,
                                        maxDevInRadius=1, CLAHE=True)
            self.video.set_goodFeaturesToTrackParams(maxCorners=50000, qualityLevel=0.001)
            self.video.set_opticalFlowParams(maxLevel=3)
            self.video.extractGoodFeaturesDisplacementsAccumulateAndInterpolate(
                display1=None, display2=None)

        # Calculate velocities ONLY within polygons/circles
        all_velocities = []
        all_points = []

        # Handle different possible structures of X and V
        if isinstance(self.video.X, list) and len(self.video.X) > 0:
            X_data = self.video.X[0]
            V_data = self.video.V[0]
        else:
            X_data = self.video.X
            V_data = self.video.V

        for j in range(len(X_data)):
            try:
                # Try different indexing methods
                if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                    x, y = X_data[j][0], X_data[j][1]
                else:
                    continue

                inside_any_shape = False

                # Check if point is in any polygon
                for polygon in self.polygons:
                    if self.point_in_polygon([x, y], polygon):
                        inside_any_shape = True
                        break

                # Check if point is in any circle
                if not inside_any_shape:
                    for circle in self.circles:
                        if self.point_in_circle([x, y], circle):
                            inside_any_shape = True
                            break

                # Only include points inside shapes
                if inside_any_shape:
                    if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                        vx = V_data[j][0]
                        vy = V_data[j][1]
                    else:
                        continue

                    magnitude = np.sqrt(vx**2 + vy**2)
                    all_velocities.append(magnitude)
                    all_points.append([x, y, vx, vy, magnitude])
            except (IndexError, TypeError):
                continue

        all_velocities = np.array(all_velocities)
        all_points = np.array(all_points)

        # Check if we have any points inside shapes
        if len(all_velocities) == 0:
            print("⚠ No velocity points found inside the drawn shapes!")
            print("  Try drawing larger polygons or circles that cover moving water areas.")
            return

        print(f"Found {len(all_velocities)} velocity points inside the drawn shapes")

        # Statistics (only from points inside shapes)
        mean_vel = np.mean(all_velocities)
        std_vel = np.std(all_velocities)
        max_vel = np.max(all_velocities)
        percentile_90 = np.percentile(all_velocities, 90)
        percentile_95 = np.percentile(all_velocities, 95)

        print(f"\nVelocity Statistics (inside shapes only):")
        print(f"  Mean: {mean_vel:.2f} px/frame")
        print(f"  Std: {std_vel:.2f} px/frame")
        print(f"  Max: {max_vel:.2f} px/frame")
        print(f"  90th percentile: {percentile_90:.2f} px/frame")
        print(f"  95th percentile: {percentile_95:.2f} px/frame")

        # Find high-velocity points (above 90th percentile)
        threshold = percentile_90
        fast_points = all_points[all_velocities > threshold]

        print(f"\nFound {len(fast_points)} points with velocity > {threshold:.2f} px/frame")

        if len(fast_points) == 0:
            print("No fast points found!")
            return

        # Cluster fast points to find main high-velocity regions
        # Simple approach: find top N fastest points and draw circles around them
        top_n = min(5, len(fast_points))  # Top 5 fastest regions
        sorted_fast = fast_points[fast_points[:, 4].argsort()[::-1]]  # Sort by magnitude descending

        # Clear previous speed visualization
        self.clear_speed_visualization()

        print(f"\nHighlighting top {top_n} fastest regions:")

        for i in range(top_n):
            point = sorted_fast[i]
            x, y, vx, vy, vel = point

            # Find cluster radius (distance to nearby fast points)
            distances = []
            for other_point in fast_points:
                dist = np.sqrt((x - other_point[0])**2 + (y - other_point[1])**2)
                if 0 < dist < 100:  # Within 100 pixels
                    distances.append(dist)

            if distances:
                radius = np.mean(distances)
            else:
                radius = 30  # Default radius

            # Ensure minimum visibility
            radius = max(radius, 20)
            radius = min(radius, 80)  # Cap at 80 pixels

            # Draw circle with intensity based on velocity
            alpha = 0.2 + (vel / max_vel) * 0.3  # Higher velocity = more opaque
            circle = Circle((x, y), radius,
                          fill=True,
                          alpha=alpha,
                          facecolor='red',
                          edgecolor='orange',
                          linewidth=3,
                          linestyle='--')
            self.ax.add_patch(circle)
            self.speed_circles.append(circle)

            # Add velocity label
            label = self.ax.text(x, y, f'{vel:.1f}',
                               ha='center', va='center',
                               color='white',
                               fontsize=10,
                               fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.3',
                                       facecolor='red',
                                       alpha=0.7))
            self.speed_circles.append(label)

            print(f"  Region {i+1}: Position ({x:.1f}, {y:.1f}), Velocity {vel:.2f} px/frame")

        self.fig.canvas.draw()
        print("\nFastest areas highlighted with RED circles!")
        print("="*50)

    def clear_speed_visualization(self, event=None):
        """Clear the speed visualization circles"""
        for artist in self.speed_circles:
            artist.remove()
        self.speed_circles = []
        self.fig.canvas.draw()
        print("Speed visualization cleared")

    def plot_flow_speed_over_time(self, event=None):
        """
        Plot flow speed over time within drawn polygons/circles
        Shows temporal evolution of flood speed
        """
        if len(self.polygons) == 0 and len(self.circles) == 0:
            print("⚠ No shapes defined. Draw polygons/circles first!")
            return

        print("\n" + "="*50)
        print("ANALYZING FLOW SPEED OVER TIME")
        print("="*50)

        # Get processing parameters (set from command line or use defaults)
        start_frame = getattr(self, 'processing_start_frame', 0)
        step = getattr(self, 'processing_step', 1)
        Ntot = getattr(self, 'processing_Ntot', 89)

        print(f"Processing configuration:")
        print(f"  Starting frame: {start_frame}")
        print(f"  Frame step: {step}")
        print(f"  Total frame pairs (Ntot): {Ntot}")
        print(f"  Will process frames {start_frame} to {start_frame + Ntot}")

        # Configure video analysis for temporal data
        print("\nExtracting velocity field over time...")
        self.video.set_vecTime(starting_frame=start_frame, step=step, shift=1, Ntot=Ntot)
        self.video.set_vlim([0, 30])
        self.video.set_filtersParams(wayBackGoodFlag=4, RadiusF=20,
                                    maxDevInRadius=1, CLAHE=True)
        self.video.set_goodFeaturesToTrackParams(maxCorners=50000, qualityLevel=0.001)
        self.video.set_opticalFlowParams(maxLevel=3)

        # Extract flow for each time step
        self.video.extractGoodFeaturesPositionsDisplacementsAndInterpolate(
            display=None)

        # Check if data was extracted
        if not hasattr(self.video, 'X') or not hasattr(self.video, 'V'):
            print("⚠ ERROR: No velocity data extracted from video!")
            return

        print(f"DEBUG: Type of self.video.X = {type(self.video.X)}")
        print(f"DEBUG: Length of self.video.X = {len(self.video.X) if hasattr(self.video.X, '__len__') else 'N/A'}")

        # Store velocity statistics over time
        time_data = []
        mean_velocities = []
        max_velocities = []
        min_velocities = []
        std_velocities = []

        # Get time vector
        if hasattr(self.video, 'Time'):
            time_vector = self.video.Time
            print(f"DEBUG: Using Time vector, length = {len(time_vector)}")
        else:
            # Create frame-based time if Time attribute doesn't exist
            if isinstance(self.video.X, list):
                time_vector = list(range(len(self.video.X)))
            else:
                time_vector = [0]  # Single time point
            print(f"DEBUG: Created time vector, length = {len(time_vector)}")

        print(f"Processing {len(time_vector)} time steps...")

        # Check if X is a list of time steps or single array
        if isinstance(self.video.X, list):
            num_time_steps = len(self.video.X)
        else:
            # Single time step - wrap in list
            self.video.X = [self.video.X]
            self.video.V = [self.video.V]
            num_time_steps = 1

        # Process each time step
        for t_idx in range(num_time_steps):
            try:
                X_data = self.video.X[t_idx]
                V_data = self.video.V[t_idx]

                velocities_at_t = []

                # Collect velocities inside shapes at this time
                for j in range(len(X_data)):
                    try:
                        if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                            x, y = X_data[j][0], X_data[j][1]
                        else:
                            continue

                        inside_any_shape = False

                        # Check if point is in any polygon
                        for polygon in self.polygons:
                            if self.point_in_polygon([x, y], polygon):
                                inside_any_shape = True
                                break

                        # Check if point is in any circle
                        if not inside_any_shape:
                            for circle in self.circles:
                                if self.point_in_circle([x, y], circle):
                                    inside_any_shape = True
                                    break

                        # Only include points inside shapes
                        if inside_any_shape:
                            if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                                vx = V_data[j][0]
                                vy = V_data[j][1]
                                magnitude = np.sqrt(vx**2 + vy**2)
                                velocities_at_t.append(magnitude)
                    except (IndexError, TypeError):
                        continue

                # Calculate statistics for this time step
                if len(velocities_at_t) > 0:
                    time_data.append(time_vector[t_idx])
                    mean_velocities.append(np.mean(velocities_at_t))
                    max_velocities.append(np.max(velocities_at_t))
                    min_velocities.append(np.min(velocities_at_t))
                    std_velocities.append(np.std(velocities_at_t))

            except (IndexError, TypeError, AttributeError) as e:
                continue

        if len(time_data) == 0:
            print("⚠ No velocity data found over time!")
            return

        print(f"✓ Processed {len(time_data)} time steps successfully")

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle('Flow Speed Over Time (Inside Drawn Shapes)', fontsize=14, fontweight='bold')

        # Plot 1: Mean, Max, Min velocities
        ax1.plot(time_data, mean_velocities, 'b-', linewidth=2, label='Mean Velocity')
        ax1.plot(time_data, max_velocities, 'r--', linewidth=1.5, label='Max Velocity')
        ax1.plot(time_data, min_velocities, 'g--', linewidth=1.5, label='Min Velocity')
        ax1.fill_between(time_data,
                         np.array(mean_velocities) - np.array(std_velocities),
                         np.array(mean_velocities) + np.array(std_velocities),
                         alpha=0.3, color='blue', label='±1 Std Dev')
        ax1.set_xlabel('Time (frame or seconds)', fontsize=11)
        ax1.set_ylabel('Velocity (px/frame)', fontsize=11)
        ax1.set_title('Velocity Statistics Over Time', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Standard deviation (variability indicator)
        ax2.plot(time_data, std_velocities, 'purple', linewidth=2, marker='o', markersize=3)
        ax2.set_xlabel('Time (frame or seconds)', fontsize=11)
        ax2.set_ylabel('Std Deviation (px/frame)', fontsize=11)
        ax2.set_title('Flow Variability Over Time', fontsize=12)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        # Print summary statistics
        print("\n" + "="*50)
        print("TEMPORAL STATISTICS SUMMARY")
        print("="*50)
        print(f"Time range: {time_data[0]:.2f} to {time_data[-1]:.2f}")
        print(f"Overall mean velocity: {np.mean(mean_velocities):.2f} px/frame")
        print(f"Peak velocity: {np.max(max_velocities):.2f} px/frame at time {time_data[np.argmax(max_velocities)]:.2f}")
        print(f"Minimum velocity: {np.min(min_velocities):.2f} px/frame at time {time_data[np.argmin(min_velocities)]:.2f}")
        print(f"Average variability (std): {np.mean(std_velocities):.2f} px/frame")
        print("="*50)

        # Save data to CSV
        csv_filename = 'flow_speed_over_time.csv'
        with open(csv_filename, 'w') as f:
            f.write('Time,Mean_Velocity,Max_Velocity,Min_Velocity,Std_Velocity\n')
            for i in range(len(time_data)):
                f.write(f'{time_data[i]},{mean_velocities[i]},{max_velocities[i]},{min_velocities[i]},{std_velocities[i]}\n')
        print(f"✓ Time series data saved to {csv_filename}")
        print("="*50 + "\n")

    def export_video_with_flow(self, event=None):
        """
        Export video showing velocity vectors overlaid on original frames
        Only shows vectors inside drawn polygons/circles
        """
        if len(self.polygons) == 0 and len(self.circles) == 0:
            print("⚠ No shapes defined. Draw polygons/circles first!")
            return

        print("\n" + "="*50)
        print("EXPORTING VIDEO WITH FLOW VISUALIZATION")
        print("="*50)

        # Get processing parameters
        start_frame = getattr(self, 'processing_start_frame', 0)
        step = getattr(self, 'processing_step', 1)
        Ntot = getattr(self, 'processing_Ntot', 100)

        print(f"Processing {Ntot} frames starting from frame {start_frame}")

        # Configure video analysis
        self.video.set_vecTime(starting_frame=start_frame, step=step, shift=1, Ntot=Ntot)
        self.video.set_vlim([0, 30])
        self.video.set_filtersParams(wayBackGoodFlag=4, RadiusF=20,
                                    maxDevInRadius=1, CLAHE=True)
        self.video.set_goodFeaturesToTrackParams(maxCorners=50000, qualityLevel=0.001)
        self.video.set_opticalFlowParams(maxLevel=3)

        # Extract flow for each time step
        print("Extracting velocity fields...")
        self.video.extractGoodFeaturesPositionsDisplacementsAndInterpolate(display=None)

        if not hasattr(self.video, 'X') or not hasattr(self.video, 'V'):
            print("⚠ ERROR: No velocity data extracted!")
            return

        # Prepare video writer
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        output_filename = 'flood_flow_visualization.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

        print(f"Creating video: {output_filename}")
        print(f"  Resolution: {width}x{height}")
        print(f"  FPS: {fps}")

        # Determine if X is list or single array
        if isinstance(self.video.X, list):
            num_time_steps = len(self.video.X)
        else:
            self.video.X = [self.video.X]
            self.video.V = [self.video.V]
            num_time_steps = 1

        # Process each frame
        for t_idx in range(num_time_steps):
            # Read corresponding frame from video
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame + t_idx)
            ret, frame = cap.read()

            if not ret:
                break

            try:
                X_data = self.video.X[t_idx]
                V_data = self.video.V[t_idx]

                # Draw polygons on frame
                for polygon in self.polygons:
                    pts = polygon.astype(np.int32)
                    cv2.polylines(frame, [pts], True, (0, 255, 255), 2)

                # Draw circles on frame
                for circle in self.circles:
                    center = (int(circle['center'][0]), int(circle['center'][1]))
                    radius = int(circle['radius'])
                    cv2.circle(frame, center, radius, (255, 255, 0), 2)

                # Draw velocity vectors (only inside shapes)
                for j in range(len(X_data)):
                    try:
                        if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                            x, y = X_data[j][0], X_data[j][1]
                        else:
                            continue

                        inside_any_shape = False

                        # Check if point is in any polygon
                        for polygon in self.polygons:
                            if self.point_in_polygon([x, y], polygon):
                                inside_any_shape = True
                                break

                        # Check if point is in any circle
                        if not inside_any_shape:
                            for circle in self.circles:
                                if self.point_in_circle([x, y], circle):
                                    inside_any_shape = True
                                    break

                        # Only draw vectors inside shapes
                        if inside_any_shape:
                            if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                                vx = V_data[j][0]
                                vy = V_data[j][1]
                                magnitude = np.sqrt(vx**2 + vy**2)

                                # Scale vector for visibility
                                scale_factor = 5
                                end_x = int(x + vx * scale_factor)
                                end_y = int(y + vy * scale_factor)

                                # Color based on magnitude (green to red)
                                if magnitude < 10:
                                    color = (0, 255, 0)  # Green - slow
                                elif magnitude < 20:
                                    color = (0, 255, 255)  # Yellow - medium
                                else:
                                    color = (0, 0, 255)  # Red - fast

                                # Draw arrow
                                cv2.arrowedLine(frame, (int(x), int(y)), (end_x, end_y),
                                               color, 2, tipLength=0.3)

                    except (IndexError, TypeError):
                        continue

                # Add frame info text
                text = f"Frame: {start_frame + t_idx}"
                cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (255, 255, 255), 2, cv2.LINE_AA)

                # Write frame
                out.write(frame)

                if (t_idx + 1) % 10 == 0:
                    print(f"  Processed {t_idx + 1}/{num_time_steps} frames...")

            except (IndexError, TypeError, AttributeError) as e:
                continue

        # Release everything
        cap.release()
        out.release()

        print(f"\n✓ Video saved to: {output_filename}")
        print("="*50 + "\n")

    def export_results(self, event=None):
        """Export velocity field and shape statistics"""
        if not hasattr(self.video, 'UxTot'):
            print("No velocity data to export. Run analysis first.")
            return

        # Export velocity field
        self.video.writeVelocityField(fileFormat='csv')
        self.video.writeVelocityField(fileFormat='hdf5')

        print("Exported velocity fields to CSV and HDF5")

        # Export shape statistics
        if len(self.polygons) > 0 or len(self.circles) > 0:
            stats_filename = 'shape_flow_statistics.json'
            stats = {'polygons': [], 'circles': []}

            # Export polygon stats
            for i, polygon in enumerate(self.polygons):
                polygon_stats = {
                    'polygon_id': i + 1,
                    'vertices': polygon.tolist(),
                    'area_px2': float(self.calculate_polygon_area(polygon))
                }

                # Add velocity statistics if available
                if hasattr(self.video, 'X') and hasattr(self.video, 'V'):
                    # Handle different possible structures of X and V
                    if isinstance(self.video.X, list) and len(self.video.X) > 0:
                        X_data = self.video.X[0]
                        V_data = self.video.V[0]
                    else:
                        X_data = self.video.X
                        V_data = self.video.V

                    velocities = []
                    for j in range(len(X_data)):
                        try:
                            if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                                x, y = X_data[j][0], X_data[j][1]
                            else:
                                continue

                            if self.point_in_polygon([x, y], polygon):
                                if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                                    vx = V_data[j][0]
                                    vy = V_data[j][1]
                                    magnitude = np.sqrt(vx**2 + vy**2)
                                    velocities.append(magnitude)
                        except (IndexError, TypeError):
                            continue

                    if len(velocities) > 0:
                        polygon_stats.update({
                            'num_points': len(velocities),
                            'mean_velocity': float(np.mean(velocities)),
                            'max_velocity': float(np.max(velocities)),
                            'min_velocity': float(np.min(velocities)),
                            'std_velocity': float(np.std(velocities))
                        })

                stats['polygons'].append(polygon_stats)

            # Export circle stats
            for i, circle in enumerate(self.circles):
                circle_stats = {
                    'circle_id': i + 1,
                    'center': list(circle['center']),
                    'radius': float(circle['radius']),
                    'area_px2': float(np.pi * circle['radius']**2)
                }

                # Add velocity statistics if available
                if hasattr(self.video, 'X') and hasattr(self.video, 'V'):
                    # Handle different possible structures of X and V
                    if isinstance(self.video.X, list) and len(self.video.X) > 0:
                        X_data = self.video.X[0]
                        V_data = self.video.V[0]
                    else:
                        X_data = self.video.X
                        V_data = self.video.V

                    velocities = []
                    for j in range(len(X_data)):
                        try:
                            if hasattr(X_data[j], '__len__') and len(X_data[j]) >= 2:
                                x, y = X_data[j][0], X_data[j][1]
                            else:
                                continue

                            if self.point_in_circle([x, y], circle):
                                if hasattr(V_data[j], '__len__') and len(V_data[j]) >= 2:
                                    vx = V_data[j][0]
                                    vy = V_data[j][1]
                                    magnitude = np.sqrt(vx**2 + vy**2)
                                    velocities.append(magnitude)
                        except (IndexError, TypeError):
                            continue

                    if len(velocities) > 0:
                        circle_stats.update({
                            'num_points': len(velocities),
                            'mean_velocity': float(np.mean(velocities)),
                            'max_velocity': float(np.max(velocities)),
                            'min_velocity': float(np.min(velocities)),
                            'std_velocity': float(np.std(velocities))
                        })

                stats['circles'].append(circle_stats)

            with open(stats_filename, 'w') as f:
                json.dump(stats, f, indent=2)

            print(f"Exported shape statistics to {stats_filename}")


def main():
    """Main function to run the interactive flood area analyzer"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Interactive Flood Area Analyzer with Speed Visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python flood_polygon_analyzer.py --video /path/to/flood_video.mp4
  python flood_polygon_analyzer.py -v /path/to/flood_video.mp4 --frame 30
  python flood_polygon_analyzer.py --help
        '''
    )

    parser.add_argument(
        '-v', '--video',
        type=str,
        help='Path to the input video file (MP4, AVI, etc.)',
        default='/Users/worakanlasudee/Documents/GitHub/Flood_speed/RIVeR/examples/data/videos/nadir/canuelas.mp4'
    )

    parser.add_argument(
        '-f', '--frame',
        type=int,
        help='Frame number to use as static background (default: 20)',
        default=20
    )

    parser.add_argument(
        '--fps',
        type=float,
        help='Frames per second for time scaling (optional)',
        default=None
    )

    parser.add_argument(
        '--scale',
        type=float,
        help='Meters per pixel for spatial scaling (optional)',
        default=None
    )

    parser.add_argument(
        '--start-frame',
        type=int,
        help='Starting frame for analysis (default: 0)',
        default=0
    )

    parser.add_argument(
        '--total-frames',
        type=int,
        help='Total number of frame pairs to process (default: auto-detect all frames)',
        default=None
    )

    parser.add_argument(
        '--step',
        type=int,
        help='Frame step between pairs (default: 1)',
        default=1
    )

    args = parser.parse_args()

    filePath = args.video
    frame_index = args.frame

    # Check if video file exists
    if not os.path.exists(filePath):
        print(f"ERROR: Video file not found: {filePath}")
        print("\nPlease provide a valid video path using:")
        print(f"  python {sys.argv[0]} --video /path/to/your/video.mp4")
        sys.exit(1)

    print("="*70)
    print("INTERACTIVE FLOOD AREA ANALYZER WITH SPEED VISUALIZATION")
    print("="*70)
    print(f"\nVideo: {os.path.basename(filePath)}")
    print(f"Full path: {filePath}")
    print(f"Background frame: {frame_index}")
    print("\nDRAWING MODES (select with radio buttons on left):")
    print("  • POLYGON MODE: Left-click to add points | Right-click to close")
    print("  • CIRCLE MODE: Left-click for center | Drag and release for radius")
    print("\nCONTROL BUTTONS (Row 1):")
    print("  • Clear Last: Remove the last drawn shape")
    print("  • Save: Save all shapes to file")
    print("  • Load: Load previously saved shapes")
    print("  • Analyze Flow: Calculate velocities within shapes")
    print("  • Show Fastest: AUTO-DETECT and highlight fastest flood areas")
    print("  • Clear Viz: Clear speed visualization")
    print("  • Export: Export all results to CSV/HDF5/JSON")
    print("\nCONTROL BUTTONS (Row 2):")
    print("  • Speed vs Time: Plot flow speed evolution over time")
    print("  • Export Video: Create video with velocity arrows overlaid")
    print("\nCOLOR CODES:")
    print("  • RED polygons = User-drawn flood areas")
    print("  • BLUE circles = User-drawn measurement circles")
    print("  • ORANGE circles = Fastest speed areas (auto-detected)")
    print("="*70 + "\n")

    # Get video info to determine total frames
    cap = cv2.VideoCapture(filePath)
    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    # Calculate Ntot (total frame pairs to process)
    if args.total_frames is not None:
        Ntot = args.total_frames
    else:
        # Auto-detect: process all available frames
        Ntot = total_video_frames - args.start_frame - 1
        if Ntot < 1:
            Ntot = 1

    print(f"\nVideo Information:")
    print(f"  Total frames in video: {total_video_frames}")
    print(f"  Video FPS: {video_fps:.2f}")
    print(f"  Duration: {total_video_frames/video_fps:.2f} seconds")
    print(f"\nProcessing Configuration:")
    print(f"  Starting frame: {args.start_frame}")
    print(f"  Frame step: {args.step}")
    print(f"  Total pairs to process (Ntot): {Ntot}")
    print(f"  This will process frames {args.start_frame} to {args.start_frame + Ntot}")

    # Create analyzer
    analyzer = FloodPolygonAnalyzer(filePath)

    # Store processing parameters
    analyzer.processing_start_frame = args.start_frame
    analyzer.processing_step = args.step
    analyzer.processing_Ntot = Ntot

    # Load first frame as static background
    print(f"\nLoading video frame {frame_index}...")
    if analyzer.load_static_frame(frame_index=frame_index):
        print("✓ Frame loaded successfully")
    else:
        print(f"ERROR: Could not load frame {frame_index} from video")
        print("The video might be shorter than expected or corrupted")
        sys.exit(1)

    # Apply scaling if provided
    if args.fps or args.scale:
        print("\nApplying data scaling...")
        fps = args.fps if args.fps else 25
        scale = args.scale if args.scale else 1.0
        print(f"  FPS: {fps}")
        print(f"  Meters per pixel: {scale}")
        # Note: Scaling will be applied after flow extraction
        analyzer.scale_fps = fps
        analyzer.scale_meters_per_px = scale
        analyzer.apply_scaling = True
    else:
        analyzer.apply_scaling = False

    # Setup interactive plot
    print("\nSetting up interactive plot...")
    analyzer.setup_interactive_plot()

    print("\n" + "="*70)
    print("✓ Ready! Select a mode and start drawing on the flood area.")
    print("✓ Click 'Show Fastest' to automatically detect high-speed regions.")
    print("✓ Click 'Speed vs Time' to see temporal evolution of flow speed.")
    print("✓ Close the plot window when finished.")
    print("="*70 + "\n")

    # Keep plot open
    plt.show(block=True)


if __name__ == "__main__":
    main()
