#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script for automated flood speed analysis
This demonstrates programmatic usage without the GUI
"""

import opyf
import numpy as np
import matplotlib.pyplot as plt
import cv2

def analyze_flood_speed(video_path, output_folder='./flood_analysis_output'):
    """
    Automated flood speed analysis

    Parameters:
    -----------
    video_path : str
        Path to video file (drone or CCTV footage)
    output_folder : str
        Where to save results
    """

    print(f"Loading video: {video_path}")

    # Create analyzer
    analyzer = opyf.videoAnalyzer(video_path, display=True, mute=False)

    print(f"Video loaded: {analyzer.number_of_frames} frames")
    print(f"Dimensions: {analyzer.frameInit.shape[1]}x{analyzer.frameInit.shape[0]}")

    # Optional: Create a mask to focus on water area only
    # For this example, we'll use the whole frame
    # To create a custom mask, uncomment below:
    # mask = np.zeros(analyzer.frameInit.shape[:2], dtype=np.uint8)
    # mask[100:500, 200:800] = 255  # Example ROI
    # analyzer.set_mask(mask)

    # Configure processing parameters
    print("\nConfiguring processing parameters...")

    # Set time vector (which frames to process)
    analyzer.set_vecTime(
        starting_frame=0,
        step=1,           # Process every frame
        shift=1,          # Shift by 1 frame
        Ntot=50           # Process 50 frame pairs
    )

    # Set velocity limits (pixels per frame)
    analyzer.set_vlim([0, 40])

    # Configure filters for better accuracy
    analyzer.set_filtersParams(
        wayBackGoodFlag=4,      # Bidirectional flow check
        RadiusF=30,             # Filter radius in pixels
        maxDevInRadius=2,       # Max deviation within radius
        CLAHE=True              # Contrast enhancement
    )

    # Set interpolation parameters
    analyzer.set_interpolationParams(
        Radius=30,
        Sharpness=8,
        kernel='Gaussian'
    )

    # Set grid for interpolation
    analyzer.set_gridToInterpolateOn(
        stepHor=5,    # Grid spacing
        stepVert=5
    )

    print("\nStarting optical flow analysis...")

    # Extract features and calculate velocities
    analyzer.extractGoodFeaturesPositionsDisplacementsAndInterpolate(
        display='field',
        Type='norm',
        saveImgPath=output_folder
    )

    print("\nAnalysis complete!")

    # Calculate statistics
    print("\n" + "="*50)
    print("FLOW SPEED STATISTICS")
    print("="*50)

    speed_stats = []
    for i, (ux, uy) in enumerate(zip(analyzer.UxTot, analyzer.UyTot)):
        speed = np.sqrt(ux**2 + uy**2)

        # Filter out invalid values
        valid_speed = speed[~np.isnan(speed)]

        if len(valid_speed) > 0:
            avg_speed = np.mean(valid_speed)
            max_speed = np.max(valid_speed)
            min_speed = np.min(valid_speed)
            std_speed = np.std(valid_speed)

            speed_stats.append({
                'frame_pair': i,
                'avg': avg_speed,
                'max': max_speed,
                'min': min_speed,
                'std': std_speed
            })

            print(f"Frame pair {i:3d}: "
                  f"Avg={avg_speed:6.2f} px/frame, "
                  f"Max={max_speed:6.2f} px/frame, "
                  f"Std={std_speed:5.2f} px/frame")

    # Overall statistics
    all_avgs = [s['avg'] for s in speed_stats]
    all_maxs = [s['max'] for s in speed_stats]

    print("\n" + "="*50)
    print(f"Overall average speed: {np.mean(all_avgs):.2f} px/frame")
    print(f"Overall max speed: {np.max(all_maxs):.2f} px/frame")
    print(f"Speed variability (std): {np.std(all_avgs):.2f} px/frame")
    print("="*50)

    # Plot temporal evolution
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    frames = [s['frame_pair'] for s in speed_stats]
    avgs = [s['avg'] for s in speed_stats]
    maxs = [s['max'] for s in speed_stats]
    stds = [s['std'] for s in speed_stats]

    # Average speed over time
    ax1.plot(frames, avgs, 'b-', linewidth=2, label='Average Speed')
    ax1.fill_between(frames,
                     np.array(avgs) - np.array(stds),
                     np.array(avgs) + np.array(stds),
                     alpha=0.3, color='blue', label='± 1 Std Dev')
    ax1.set_xlabel('Frame Pair')
    ax1.set_ylabel('Speed (px/frame)')
    ax1.set_title('Average Flow Speed Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Max speed over time
    ax2.plot(frames, maxs, 'r-', linewidth=2, label='Max Speed')
    ax2.set_xlabel('Frame Pair')
    ax2.set_ylabel('Speed (px/frame)')
    ax2.set_title('Maximum Flow Speed Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_folder}/speed_temporal_analysis.png', dpi=150)
    print(f"\nTemporal analysis saved to: {output_folder}/speed_temporal_analysis.png")

    # Export results
    print("\nExporting results...")

    # Export to CSV
    analyzer.writeVelocityField(
        fileFormat='csv',
        outFolder=output_folder,
        filename='flood_velocity_field'
    )

    # Export to HDF5
    analyzer.writeVelocityField(
        fileFormat='hdf5',
        outFolder=output_folder,
        filename='flood_velocity_field'
    )

    print(f"Results exported to: {output_folder}/")
    print("\nDone!")

    return analyzer, speed_stats


if __name__ == '__main__':
    # Example usage
    import os

    # Modify this path to your video file
    video_path = "/Users/worakanlasudee/Documents/GitHub/Flood_speed/RIVeR/examples/data/videos/nadir/canuelas.mp4"

    # Create output directory
    output_dir = './flood_analysis_results'
    os.makedirs(output_dir, exist_ok=True)

    # Run analysis
    if os.path.exists(video_path):
        analyzer, stats = analyze_flood_speed(video_path, output_dir)
        plt.show()
    else:
        print(f"Error: Video file not found at {video_path}")
        print("Please update the video_path variable with your video file location")
