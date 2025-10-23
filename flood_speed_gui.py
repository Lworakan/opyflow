#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flood Speed Analysis GUI
Automated water flow speed calculation with area selection and temporal visualization
Supports drone and CCTV camera footage
"""

import sys
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog,
                             QSpinBox, QDoubleSpinBox, QGroupBox, QGridLayout,
                             QCheckBox, QMessageBox, QTabWidget, QTextEdit,
                             QComboBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import opyf
from datetime import datetime, timedelta
import json


class VideoProcessor(QThread):
    """Background thread for processing video with optical flow"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    log = pyqtSignal(str)

    def __init__(self, analyzer, processing_params, is_quick_test=False):
        super().__init__()
        self.analyzer = analyzer
        self.params = processing_params
        self.is_quick_test = is_quick_test

    def run(self):
        try:
            if self.is_quick_test:
                # Quick test with detailed steps
                self.log.emit("-" * 50)
                self.log.emit("[Step 2 / 7] Setting time vector...")
                self.log.emit("-" * 50)

            self.log.emit("Starting optical flow analysis...")
            self.log.emit(f"Processing {self.params['Ntot']} frame pairs...")

            # Configure analyzer
            self.analyzer.set_vecTime(
                starting_frame=self.params['starting_frame'],
                step=self.params['step'],
                shift=self.params['shift'],
                Ntot=self.params['Ntot']
            )

            if self.is_quick_test:
                self.log.emit(f"✓ Will process {self.params['Ntot']} frame pairs (step={self.params['step']}, shift={self.params['shift']})")
                self.log.emit("-" * 50)
                self.log.emit("[Step 3 / 7] Setting velocity limits...")
                self.log.emit("-" * 50)

            self.analyzer.set_vlim(self.params['vlim'])

            if self.is_quick_test:
                self.log.emit(f"✓ Velocity range: {self.params['vlim'][0]}-{self.params['vlim'][1]} px/frame")
                self.log.emit("-" * 50)
                self.log.emit("[Step 4 / 7] Configuring filters...")
                self.log.emit("-" * 50)

            self.analyzer.set_filtersParams(
                wayBackGoodFlag=self.params['wayBackGoodFlag'],
                RadiusF=self.params['RadiusF'],
                maxDevInRadius=self.params['maxDevInRadius'],
                CLAHE=self.params['CLAHE']
            )

            if self.is_quick_test:
                self.log.emit(f"✓ Filters: wayBackGoodFlag={self.params['wayBackGoodFlag']}, RadiusF={self.params['RadiusF']}, CLAHE={'ON' if self.params['CLAHE'] else 'OFF'}")
                self.log.emit("-" * 50)
                self.log.emit("[Step 5 / 7] Processing optical flow...")
                self.log.emit("-" * 50)
                self.log.emit("This will take a moment...")

            # Extract features and displacements
            self.analyzer.extractGoodFeaturesPositionsDisplacementsAndInterpolate(
                display=False
            )

            self.log.emit("✓ Processing complete!")
            self.finished.emit(self.analyzer)

        except Exception as e:
            self.log.emit(f"Error during processing: {str(e)}")


class MaskDrawer:
    """Interactive mask/ROI drawing tool"""
    def __init__(self, frame):
        self.frame = frame.copy()
        self.mask = np.ones(frame.shape[:2], dtype=np.uint8) * 255
        self.drawing = False
        self.mode = 'polygon'  # 'polygon' or 'rectangle'
        self.points = []
        self.current_roi = None

    def draw_polygon(self):
        """Interactive polygon drawing for selecting water area"""
        cv2.namedWindow('Draw Water Area - Click to add points, Press ENTER when done, ESC to cancel')
        cv2.setMouseCallback('Draw Water Area - Click to add points, Press ENTER when done, ESC to cancel', self.mouse_callback)

        temp_frame = self.frame.copy()
        while True:
            display_frame = temp_frame.copy()

            # Draw current polygon
            if len(self.points) > 0:
                pts = np.array(self.points, np.int32)
                cv2.polylines(display_frame, [pts], False, (0, 255, 0), 2)

            # Draw points
            for pt in self.points:
                cv2.circle(display_frame, pt, 5, (0, 0, 255), -1)

            cv2.imshow('Draw Water Area - Click to add points, Press ENTER when done, ESC to cancel', display_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 13:  # Enter key
                if len(self.points) > 2:
                    # Create mask
                    self.mask = np.zeros(self.frame.shape[:2], dtype=np.uint8)
                    pts = np.array(self.points, np.int32)
                    cv2.fillPoly(self.mask, [pts], 255)
                    break
            elif key == 27:  # ESC key
                self.mask = np.ones(self.frame.shape[:2], dtype=np.uint8) * 255
                break

        cv2.destroyAllWindows()
        return self.mask

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))

    def draw_rectangle(self):
        """Interactive rectangle drawing for ROI"""
        roi = cv2.selectROI('Select Region of Interest - Press ENTER when done',
                           self.frame, showCrosshair=True)
        cv2.destroyAllWindows()

        if roi[2] > 0 and roi[3] > 0:
            self.current_roi = [roi[0], roi[1], roi[2], roi[3]]
            # Create mask for rectangle
            self.mask = np.zeros(self.frame.shape[:2], dtype=np.uint8)
            self.mask[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]] = 255

        return self.current_roi, self.mask


class FloodSpeedGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flood Speed Analysis Tool")
        self.setGeometry(100, 100, 1600, 900)

        # Data storage
        self.video_path = None
        self.analyzer = None
        self.mask = None
        self.roi = None
        self.processing_results = None
        self.frame_times = []  # For hourly analysis
        self.speed_data = []  # Time series of flow speeds
        self._colorbar = None  # Store colorbar reference

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, stretch=1)

        # Right panel - Visualization
        right_panel = self.create_visualization_panel()
        main_layout.addWidget(right_panel, stretch=3)

    def create_control_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Video input section
        input_group = QGroupBox("1. Video Input")
        input_layout = QVBoxLayout()

        self.load_video_btn = QPushButton("Load Video (Drone/CCTV)")
        self.load_video_btn.clicked.connect(self.load_video)
        input_layout.addWidget(self.load_video_btn)

        self.video_info_label = QLabel("No video loaded")
        self.video_info_label.setWordWrap(True)
        input_layout.addWidget(self.video_info_label)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # ROI and Mask section
        roi_group = QGroupBox("2. Select Water Area")
        roi_layout = QVBoxLayout()

        self.select_roi_btn = QPushButton("Select Rectangle ROI")
        self.select_roi_btn.clicked.connect(self.select_roi)
        self.select_roi_btn.setEnabled(False)
        roi_layout.addWidget(self.select_roi_btn)

        self.draw_mask_btn = QPushButton("Draw Polygon Water Area")
        self.draw_mask_btn.clicked.connect(self.draw_water_mask)
        self.draw_mask_btn.setEnabled(False)
        roi_layout.addWidget(self.draw_mask_btn)

        self.mask_status_label = QLabel("No area selected")
        roi_layout.addWidget(self.mask_status_label)

        roi_group.setLayout(roi_layout)
        layout.addWidget(roi_group)

        # Processing parameters
        params_group = QGroupBox("3. Processing Parameters")
        params_layout = QGridLayout()

        # Frame range
        params_layout.addWidget(QLabel("Start Frame:"), 0, 0)
        self.start_frame_spin = QSpinBox()
        self.start_frame_spin.setMinimum(0)
        self.start_frame_spin.setValue(0)
        params_layout.addWidget(self.start_frame_spin, 0, 1)

        params_layout.addWidget(QLabel("Frame Step:"), 1, 0)
        self.step_spin = QSpinBox()
        self.step_spin.setMinimum(1)
        self.step_spin.setMaximum(10)
        self.step_spin.setValue(1)
        params_layout.addWidget(self.step_spin, 1, 1)

        params_layout.addWidget(QLabel("Frame Shift:"), 2, 0)
        self.shift_spin = QSpinBox()
        self.shift_spin.setMinimum(1)
        self.shift_spin.setMaximum(10)
        self.shift_spin.setValue(1)
        params_layout.addWidget(self.shift_spin, 2, 1)

        params_layout.addWidget(QLabel("Total Pairs:"), 3, 0)
        self.ntot_spin = QSpinBox()
        self.ntot_spin.setMinimum(1)
        self.ntot_spin.setMaximum(10000)
        self.ntot_spin.setValue(10)
        params_layout.addWidget(self.ntot_spin, 3, 1)

        # Velocity limits
        params_layout.addWidget(QLabel("Min Speed (px):"), 4, 0)
        self.vmin_spin = QDoubleSpinBox()
        self.vmin_spin.setMinimum(0)
        self.vmin_spin.setMaximum(1000)
        self.vmin_spin.setValue(0)
        params_layout.addWidget(self.vmin_spin, 4, 1)

        params_layout.addWidget(QLabel("Max Speed (px):"), 5, 0)
        self.vmax_spin = QDoubleSpinBox()
        self.vmax_spin.setMinimum(0)
        self.vmax_spin.setMaximum(1000)
        self.vmax_spin.setValue(50)
        params_layout.addWidget(self.vmax_spin, 5, 1)

        # Filter parameters
        params_layout.addWidget(QLabel("Filter Radius:"), 6, 0)
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setMinimum(1)
        self.radius_spin.setMaximum(200)
        self.radius_spin.setValue(30)
        params_layout.addWidget(self.radius_spin, 6, 1)

        self.clahe_check = QCheckBox("Enable CLAHE")
        self.clahe_check.setChecked(True)
        params_layout.addWidget(self.clahe_check, 7, 0, 1, 2)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Processing control
        process_group = QGroupBox("4. Process Video")
        process_layout = QVBoxLayout()

        self.process_btn = QPushButton("Start Analysis")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        self.process_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        process_layout.addWidget(self.process_btn)

        self.quick_test_btn = QPushButton("Quick Test (Canuelas Video)")
        self.quick_test_btn.clicked.connect(self.run_quick_test)
        self.quick_test_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 10px; }")
        process_layout.addWidget(self.quick_test_btn)

        self.progress_bar = QProgressBar()
        process_layout.addWidget(self.progress_bar)

        process_group.setLayout(process_layout)
        layout.addWidget(process_group)

        # Export section
        export_group = QGroupBox("5. Export Results")
        export_layout = QVBoxLayout()

        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_results('csv'))
        self.export_csv_btn.setEnabled(False)
        export_layout.addWidget(self.export_csv_btn)

        self.export_hdf5_btn = QPushButton("Export to HDF5")
        self.export_hdf5_btn.clicked.connect(lambda: self.export_results('hdf5'))
        self.export_hdf5_btn.setEnabled(False)
        export_layout.addWidget(self.export_hdf5_btn)

        self.save_frame_btn = QPushButton("Save Current Frame")
        self.save_frame_btn.clicked.connect(self.save_current_frame_visualization)
        self.save_frame_btn.setEnabled(False)
        export_layout.addWidget(self.save_frame_btn)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Log area
        log_group = QGroupBox("Processing Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        layout.addStretch()
        return panel

    def create_visualization_panel(self):
        """Create right visualization panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for different visualizations
        self.tabs = QTabWidget()

        # Tab 1: Current frame with flow vectors
        self.flow_canvas = MplCanvas(self, width=8, height=6, dpi=100)
        self.tabs.addTab(self.flow_canvas, "Flow Vectors")

        # Tab 2: Speed field visualization
        self.field_canvas = MplCanvas(self, width=8, height=6, dpi=100)
        self.tabs.addTab(self.field_canvas, "Velocity Field")

        # Tab 3: Temporal analysis
        self.temporal_canvas = MplCanvas(self, width=8, height=6, dpi=100)
        self.tabs.addTab(self.temporal_canvas, "Time Series")

        layout.addWidget(self.tabs)

        # Timeline slider
        timeline_group = QGroupBox("Timeline Control")
        timeline_layout = QVBoxLayout()

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Frame:"))

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(0)
        self.time_slider.valueChanged.connect(self.on_slider_change)
        slider_layout.addWidget(self.time_slider)

        self.frame_label = QLabel("0 / 0")
        slider_layout.addWidget(self.frame_label)

        timeline_layout.addLayout(slider_layout)

        # Speed display
        speed_layout = QHBoxLayout()
        self.avg_speed_label = QLabel("Avg Speed: -- px/frame")
        self.max_speed_label = QLabel("Max Speed: -- px/frame")
        speed_layout.addWidget(self.avg_speed_label)
        speed_layout.addWidget(self.max_speed_label)
        timeline_layout.addLayout(speed_layout)

        timeline_group.setLayout(timeline_layout)
        layout.addWidget(timeline_group)

        return panel

    def load_video(self):
        """Load video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )

        if file_path:
            try:
                self.video_path = file_path
                self.log_message(f"Loading video: {os.path.basename(file_path)}")

                # Create analyzer
                self.analyzer = opyf.videoAnalyzer(file_path, display=False, mute=True)

                # Update UI
                num_frames = self.analyzer.number_of_frames
                width = self.analyzer.frameInit.shape[1]
                height = self.analyzer.frameInit.shape[0]

                self.video_info_label.setText(
                    f"Video: {os.path.basename(file_path)}\n"
                    f"Frames: {num_frames}\n"
                    f"Size: {width}x{height}"
                )

                self.start_frame_spin.setMaximum(num_frames - 2)
                self.ntot_spin.setMaximum(num_frames - 1)

                # Enable ROI selection
                self.select_roi_btn.setEnabled(True)
                self.draw_mask_btn.setEnabled(True)

                # Show first frame
                self.show_initial_frame()

                self.log_message("Video loaded successfully!")

            except Exception as e:
                self.log_message(f"Error loading video: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to load video:\n{str(e)}")

    def show_initial_frame(self):
        """Display the first frame"""
        if self.analyzer:
            frame = self.analyzer.frameInit
            self.flow_canvas.axes.clear()
            self.flow_canvas.axes.imshow(frame, cmap='gray')
            self.flow_canvas.axes.set_title("First Frame - Ready for ROI Selection")
            self.flow_canvas.axes.axis('off')
            self.flow_canvas.draw()

    def select_roi(self):
        """Select rectangular ROI"""
        if self.analyzer is None:
            return

        self.log_message("Select rectangle ROI...")
        drawer = MaskDrawer(self.analyzer.frameInit)
        roi, mask = drawer.draw_rectangle()

        if roi is not None:
            self.roi = roi
            self.mask = mask
            self.analyzer.ROI = roi
            self.analyzer.set_mask(mask)

            self.mask_status_label.setText(
                f"ROI: ({roi[0]}, {roi[1]}, {roi[2]}, {roi[3]})"
            )
            self.process_btn.setEnabled(True)
            self.log_message("ROI selected successfully!")

    def draw_water_mask(self):
        """Draw polygon mask for water area"""
        if self.analyzer is None:
            return

        self.log_message("Draw polygon around water area...")

        # Draw on the cropped frame (what the analyzer actually uses)
        drawer = MaskDrawer(self.analyzer.cropFrameInit)
        mask = drawer.draw_polygon()

        # The mask is already in the right dimensions (cropFrameInit size)
        self.mask = mask
        self.analyzer.set_mask(mask)

        self.mask_status_label.setText("Custom polygon mask created")
        self.process_btn.setEnabled(True)
        self.log_message("Water area mask created successfully!")

    def run_quick_test(self):
        """Run quick test with canuelas video using test_opyf_Navizence.py pipeline"""
        self.log_message("=" * 50)
        self.log_message("QUICK TEST - Processing All Frames")
        self.log_message("=" * 50)

        # Video path
        test_video = '/Users/worakanlasudee/Documents/GitHub/Flood_speed/RIVeR/examples/data/videos/nadir/canuelas.mp4'

        if not os.path.exists(test_video):
            self.log_message(f"Error: Test video not found at {test_video}")
            QMessageBox.warning(self, "Video Not Found",
                              f"Test video not found:\n{test_video}\n\nPlease update the path.")
            return

        try:
            # Step 1
            self.log_message("-" * 50)
            self.log_message("[Step 1 / 7] Loading test video...")
            self.log_message("-" * 50)
            self.analyzer = opyf.videoAnalyzer(test_video, display=False, mute=True)
            self.video_path = test_video

            # Update UI
            self.video_info_label.setText(
                f"Video: canuelas.mp4 (TEST)\n"
                f"Frames: {self.analyzer.number_of_frames}\n"
                f"Size: {self.analyzer.frameInit.shape[1]}x{self.analyzer.frameInit.shape[0]}"
            )
            self.log_message(f"✓ Video loaded: {self.analyzer.number_of_frames} frames")

            # Step 2
            self.log_message("-" * 50)
            self.log_message("[Step 2 / 7] Setting time vector...")
            self.log_message("-" * 50)
            # Process ALL frames (0 to 89)
            self.analyzer.set_vecTime(
                starting_frame=0,
                step=1,        # Process every frame
                shift=1,
                Ntot=89        # 90 frames total (0-89)
            )
            self.log_message(f"✓ Will process {89} frame pairs (step=1, shift=1)")

            # Step 3
            self.log_message("-" * 50)
            self.log_message("[Step 3 / 7] Setting velocity limits...")
            self.log_message("-" * 50)
            self.analyzer.set_vlim([0, 30])
            self.log_message("✓ Velocity range: 0-30 px/frame")

            # Step 4
            self.log_message("-" * 50)
            self.log_message("[Step 4 / 7] Configuring filters...")
            self.log_message("-" * 50)
            self.analyzer.set_filtersParams(
                wayBackGoodFlag=4,
                RadiusF=20,
                maxDevInRadius=1,
                CLAHE=True
            )
            self.log_message("✓ Filters: wayBackGoodFlag=4, RadiusF=20, CLAHE=ON")

            # Step 5
            self.log_message("-" * 50)
            self.log_message("[Step 5 / 7] Setting feature detection params...")
            self.log_message("-" * 50)
            self.analyzer.set_goodFeaturesToTrackParams(
                maxCorners=50000,
                qualityLevel=0.001
            )
            self.analyzer.set_opticalFlowParams(maxLevel=3)
            self.log_message("✓ Features: maxCorners=50000, qualityLevel=0.001")

            # Step 6
            self.log_message("-" * 50)
            self.log_message("[Step 6 / 7] Processing optical flow...")
            self.log_message("-" * 50)
            self.log_message("This will take a moment - processing 89 frame pairs...")
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(10)

            self.analyzer.extractGoodFeaturesPositionsDisplacementsAndInterpolate(
                display=False
            )

            self.progress_bar.setValue(100)
            self.log_message("✓ Optical flow analysis complete!")

            # Store results
            self.processing_results = self.analyzer

            # Step 7
            self.log_message("-" * 50)
            self.log_message("[Step 7 / 7] Generating visualizations...")
            self.log_message("-" * 50)

            # Calculate statistics
            self.calculate_speed_statistics()
            self.log_message(f"✓ Calculated statistics for {len(self.speed_data)} frames")

            # Enable timeline
            num_results = len(self.processing_results.UxTot)
            self.time_slider.setMaximum(num_results - 1)
            self.frame_label.setText(f"0 / {num_results - 1}")

            # Visualize
            self.visualize_current_field(0)
            self.visualize_temporal_analysis()
            self.log_message("✓ Visualizations generated")

            # Enable export
            self.export_csv_btn.setEnabled(True)
            self.export_hdf5_btn.setEnabled(True)
            self.save_frame_btn.setEnabled(True)

            self.log_message("=" * 50)
            self.log_message("✓ QUICK TEST COMPLETE!")
            self.log_message("=" * 50)
            self.log_message("Use the timeline slider to explore all 89 frame pairs")
            self.log_message("Check 'Velocity Field' tab to see flow vectors")
            self.log_message("Check 'Time Series' tab to see temporal analysis")

        except Exception as e:
            self.log_message("=" * 50)
            self.log_message(f"✗ Test failed: {str(e)}")
            self.log_message("=" * 50)
            QMessageBox.critical(self, "Test Failed", f"Quick test failed:\n{str(e)}")

    def start_processing(self):
        """Start optical flow processing"""
        if self.analyzer is None:
            return

        self.log_message("=" * 50)
        self.log_message("Starting processing...")

        # Disable controls
        self.process_btn.setEnabled(False)
        self.load_video_btn.setEnabled(False)

        # Get parameters
        params = {
            'starting_frame': self.start_frame_spin.value(),
            'step': self.step_spin.value(),
            'shift': self.shift_spin.value(),
            'Ntot': self.ntot_spin.value(),
            'vlim': [self.vmin_spin.value(), self.vmax_spin.value()],
            'wayBackGoodFlag': 4,
            'RadiusF': self.radius_spin.value(),
            'maxDevInRadius': 2,
            'CLAHE': self.clahe_check.isChecked()
        }

        # Start processing thread
        self.processor = VideoProcessor(self.analyzer, params)
        self.processor.log.connect(self.log_message)
        self.processor.finished.connect(self.on_processing_complete)
        self.processor.start()

    def on_processing_complete(self, analyzer):
        """Called when processing is complete"""
        self.processing_results = analyzer
        self.log_message("Processing complete! Generating visualizations...")

        # Enable timeline slider
        num_results = len(self.processing_results.UxTot)
        self.time_slider.setMaximum(num_results - 1)
        self.frame_label.setText(f"0 / {num_results - 1}")

        # Calculate speed time series
        self.calculate_speed_statistics()

        # Visualize results
        self.visualize_current_field(0)
        self.visualize_temporal_analysis()

        # Enable export
        self.export_csv_btn.setEnabled(True)
        self.export_hdf5_btn.setEnabled(True)
        self.save_frame_btn.setEnabled(True)

        # Re-enable controls
        self.process_btn.setEnabled(True)
        self.load_video_btn.setEnabled(True)

        self.log_message("All done! Use the slider to explore results.")

    def calculate_speed_statistics(self):
        """Calculate flow speed statistics over time"""
        if self.processing_results is None:
            return

        self.speed_data = []

        for i in range(len(self.processing_results.UxTot)):
            ux = self.processing_results.UxTot[i]
            uy = self.processing_results.UyTot[i]

            # Calculate speed magnitude
            speed = np.sqrt(ux**2 + uy**2)

            # Apply mask
            masked_speed = speed[self.processing_results.gridMask]

            # Statistics
            valid_speeds = masked_speed[~np.isnan(masked_speed)]
            if len(valid_speeds) > 0:
                avg_speed = np.mean(valid_speeds)
                max_speed = np.max(valid_speeds)
                std_speed = np.std(valid_speeds)
            else:
                avg_speed = max_speed = std_speed = 0

            self.speed_data.append({
                'frame_index': i,
                'avg_speed': avg_speed,
                'max_speed': max_speed,
                'std_speed': std_speed
            })

    def visualize_current_field(self, index):
        """Visualize velocity field using opyf's built-in display method"""
        if self.processing_results is None or index >= len(self.processing_results.UxTot):
            return

        # Get the corresponding video frame
        frame_idx = self.processing_results.vec[index * 2] if index * 2 < len(self.processing_results.vec) else 0
        self.processing_results.readFrame(frame_idx)

        # Use opyf's native rendering
        from opyf import Render

        # Get velocity field
        gridVx = self.processing_results.UxTot[index]
        gridVy = self.processing_results.UyTot[index]
        Field = Render.setField(gridVx, gridVy, 'norm')

        # Clear the figure
        self.field_canvas.fig.clear()
        self.field_canvas.axes = self.field_canvas.fig.add_subplot(111)

        # Show background frame
        vis_rgb = cv2.cvtColor(self.processing_results.vis, cv2.COLOR_BGR2RGB)
        extent = self.processing_results.paramPlot['extentFrame']
        self.field_canvas.axes.imshow(vis_rgb, extent=extent, zorder=0)

        # Overlay velocity field
        grid_x = self.processing_results.grid_x
        grid_y = self.processing_results.grid_y
        resx = np.absolute(grid_x[0, 1] - grid_x[0, 0])
        resy = np.absolute(grid_y[1, 0] - grid_y[0, 0])
        field_extent = [
            grid_x[0, 0] - resx/2,
            grid_x[0, -1] + resx/2,
            grid_y[-1, 0] - resy/2,
            grid_y[0, 0] + resy/2
        ]

        vlim = self.processing_results.paramPlot['vlim']
        im = self.field_canvas.axes.imshow(
            Field,
            extent=field_extent,
            cmap='jet',
            alpha=0.6,
            interpolation='bilinear',
            vmin=vlim[0],
            vmax=vlim[1],
            zorder=1
        )

        # Plot velocity vectors if available
        if hasattr(self.processing_results, 'xTot') and index < len(self.processing_results.xTot):
            x_pos = self.processing_results.xTot[index]
            y_pos = self.processing_results.yTot[index]
            dx = self.processing_results.dxTot[index]
            dy = self.processing_results.dyTot[index]

            valid = ~np.isnan(dx) & ~np.isnan(dy)
            if np.sum(valid) > 0:
                velocity_mag = np.sqrt(dx[valid]**2 + dy[valid]**2)

                self.field_canvas.axes.quiver(
                    x_pos[valid], y_pos[valid], dx[valid], dy[valid],
                    velocity_mag,
                    cmap='jet',
                    scale=self.processing_results.paramPlot.get('scale', 80),
                    width=0.002,
                    headwidth=3,
                    headlength=4,
                    alpha=0.8,
                    clim=[vlim[0], vlim[1]],
                    zorder=2
                )

                self.log_message(f"Displayed {np.sum(valid)} velocity vectors")

        # Add colorbar
        unit_str = '/'.join(self.processing_results.unit)
        cbar = self.field_canvas.fig.colorbar(
            im,
            ax=self.field_canvas.axes,
            label=f'norm velocity ({unit_str})'
        )

        # Labels and title
        self.field_canvas.axes.set_xlabel('X [px]')
        self.field_canvas.axes.set_ylabel('Y [px]')
        self.field_canvas.axes.set_title(f"norm velocity - Frame {frame_idx}")
        self.field_canvas.axes.grid(True, color='white', alpha=0.3, linewidth=0.5)

        # Update canvas
        self.field_canvas.draw()

        # Update speed labels
        stats = self.speed_data[index]
        self.avg_speed_label.setText(f"Avg Speed: {stats['avg_speed']:.2f} px/frame")
        self.max_speed_label.setText(f"Max Speed: {stats['max_speed']:.2f} px/frame")

    def visualize_temporal_analysis(self):
        """Visualize temporal trends"""
        if not self.speed_data:
            return

        frames = [d['frame_index'] for d in self.speed_data]
        avg_speeds = [d['avg_speed'] for d in self.speed_data]
        max_speeds = [d['max_speed'] for d in self.speed_data]
        std_speeds = [d['std_speed'] for d in self.speed_data]

        self.temporal_canvas.axes.clear()
        self.temporal_canvas.axes.plot(frames, avg_speeds, 'b-', label='Average Speed', linewidth=2)
        self.temporal_canvas.axes.plot(frames, max_speeds, 'r-', label='Max Speed', linewidth=2)
        self.temporal_canvas.axes.fill_between(frames,
                                               np.array(avg_speeds) - np.array(std_speeds),
                                               np.array(avg_speeds) + np.array(std_speeds),
                                               alpha=0.3, label='Std Dev')
        self.temporal_canvas.axes.set_xlabel('Frame Pair Index')
        self.temporal_canvas.axes.set_ylabel('Speed (px/frame)')
        self.temporal_canvas.axes.set_title('Flow Speed Over Time')
        self.temporal_canvas.axes.legend()
        self.temporal_canvas.axes.grid(True, alpha=0.3)
        self.temporal_canvas.draw()

    def on_slider_change(self, value):
        """Handle timeline slider change"""
        if self.processing_results is not None:
            self.frame_label.setText(f"{value} / {self.time_slider.maximum()}")
            self.visualize_current_field(value)

    def export_results(self, format_type):
        """Export results to file"""
        if self.processing_results is None:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Results as {format_type.upper()}",
            f"flood_speed_results.{format_type}",
            f"{format_type.upper()} Files (*.{format_type})"
        )

        if save_path:
            try:
                self.log_message(f"Exporting to {format_type}...")

                if format_type == 'csv':
                    self.processing_results.writeVelocityField(
                        fileFormat='csv',
                        outFolder=os.path.dirname(save_path),
                        filename=os.path.splitext(os.path.basename(save_path))[0]
                    )
                elif format_type == 'hdf5':
                    self.processing_results.writeVelocityField(
                        fileFormat='hdf5',
                        outFolder=os.path.dirname(save_path),
                        filename=os.path.splitext(os.path.basename(save_path))[0]
                    )

                # Also export speed statistics
                stats_path = save_path.replace(f'.{format_type}', '_statistics.json')
                with open(stats_path, 'w') as f:
                    json.dump(self.speed_data, f, indent=2)

                self.log_message(f"Export complete: {save_path}")
                QMessageBox.information(self, "Success", f"Results exported to:\n{save_path}")

            except Exception as e:
                self.log_message(f"Export failed: {str(e)}")
                QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")

    def save_current_frame_visualization(self):
        """Save the current frame visualization as PNG"""
        if self.processing_results is None:
            return

        current_index = self.time_slider.value()
        frame_idx = self.processing_results.vec[current_index * 2] if current_index * 2 < len(self.processing_results.vec) else 0

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Frame Visualization",
            f"frame_{frame_idx}_velocity_field.png",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )

        if save_path:
            try:
                self.log_message(f"Saving frame {frame_idx} visualization...")
                self.field_canvas.fig.savefig(save_path, dpi=150, bbox_inches='tight')
                self.log_message(f"Frame saved: {save_path}")
                QMessageBox.information(self, "Success", f"Frame visualization saved to:\n{save_path}")
            except Exception as e:
                self.log_message(f"Save failed: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to save frame:\n{str(e)}")

    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")


class MplCanvas(FigureCanvas):
    """Matplotlib canvas for PyQt"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look

    window = FloodSpeedGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
