#!/usr/bin/env python3
"""
Example: Calculate and Apply Windowing to InBreast Dataset

This script demonstrates how to:
1. Calculate optimal windowing parameters from DICOM files
2. Apply windowing transformation
3. Visualize results

Usage:
    python example_windowing.py
"""

import numpy as np
import pydicom
from pathlib import Path
import matplotlib.pyplot as plt
from calculate_windowing import (
    calculate_windowing,
    analyze_dataset_windowing,
    compare_methods_on_dataset,
    print_windowing_report,
    save_windowing_report,
    get_mammography_preset,
    calculate_all_methods
)
from windowing import apply_windowing


def visualize_windowing_comparison(image, methods_results):
    """
    Create a comparison visualization of different windowing methods.
    """
    num_methods = len(methods_results)
    cols = 3
    rows = (num_methods + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 4))
    axes = axes.flatten() if num_methods > 1 else [axes]
    
    for idx, (method, (center, width)) in enumerate(methods_results.items()):
        if center is None:
            continue
            
        # Apply windowing
        windowed = apply_windowing(
            image.copy(),
            window_center=center,
            window_width=width,
            voi_func='LINEAR',
            y_min=0,
            y_max=image.max(),
            backend='np_v2'
        )
        
        # Display
        axes[idx].imshow(windowed, cmap='gray', vmin=0, vmax=windowed.max())
        axes[idx].set_title(f'{method}\nC:{center} W:{width}', fontsize=10)
        axes[idx].axis('off')
    
    # Hide unused subplots
    for idx in range(num_methods, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    return fig


def example_single_image():
    """
    Example: Calculate windowing for a single image.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Single Image Windowing")
    print("=" * 70)
    
    # Load a sample DICOM
    inbreast_dir = Path("/home/eloygarcia/Escritorio/Datasets/inbreast/ALL-IMGS")
    sample_dcm = list(inbreast_dir.glob("*.dcm"))[0]
    
    print(f"\nLoading: {sample_dcm.name}")
    
    dcm = pydicom.dcmread(sample_dcm)
    image = dcm.pixel_array
    
    print(f"Image shape: {image.shape}")
    print(f"Pixel value range: {image.min()} - {image.max()}")
    
    # Calculate using different methods
    print("\n" + "-" * 70)
    print("Calculating windowing parameters with all methods:")
    print("-" * 70)
    
    results = calculate_all_methods(image)
    
    for method, (center, width) in results.items():
        if center is not None:
            print(f"{method:20s} | Center: {center:5d} | Width: {width:5d}")
    
    # Visualize comparison
    print("\nGenerating comparison visualization...")
    fig = visualize_windowing_comparison(image, results)
    output_path = Path("windowing_comparison.png")
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved to: {output_path}")
    plt.close()
    
    # Recommend best method
    recommended_method = get_mammography_preset('breast_optimized')
    center, width = calculate_windowing(image, method=recommended_method)
    print(f"\n✓ RECOMMENDED for mammography: {recommended_method}")
    print(f"  Window Center: {center}")
    print(f"  Window Width: {width}")
    
    return center, width


def example_dataset_analysis():
    """
    Example: Analyze windowing parameters across entire dataset.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Dataset-wide Windowing Analysis")
    print("=" * 70)
    
    # Get DICOM files
    inbreast_dir = Path("/home/eloygarcia/Escritorio/Datasets/inbreast/ALL-IMGS")
    dicom_files = list(inbreast_dir.glob("*.dcm"))
    
    print(f"\nFound {len(dicom_files)} DICOM files")
    print(f"Sampling 50 images for analysis...")
    
    # Analyze with recommended method
    method = get_mammography_preset('breast_optimized')
    stats = analyze_dataset_windowing(dicom_files[:50], method=method)
    
    # Print report
    print_windowing_report(stats, "InBreast Dataset - Windowing Analysis")
    
    # Save to file
    output_path = Path("../../vendors/Siemens/inbreast_windowing_statistics.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_windowing_report(stats, output_path)
    
    return stats


def example_method_comparison():
    """
    Example: Compare all methods on the dataset.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Method Comparison on Dataset")
    print("=" * 70)
    
    # Get DICOM files
    inbreast_dir = Path("/home/eloygarcia/Escritorio/Datasets/inbreast/ALL-IMGS")
    dicom_files = list(inbreast_dir.glob("*.dcm"))[:30]  # Sample 30 for speed
    
    print(f"\nComparing methods on {len(dicom_files)} images...")
    
    # Compare all methods
    results = compare_methods_on_dataset(dicom_files, num_samples=30)
    
    # Print summary
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Method':<25} {'Center':<15} {'Width':<15} {'Std Dev'}")
    print("-" * 70)
    
    for method, stats in results.items():
        if stats:
            center = f"{stats['avg_center']} ± {stats['std_center']}"
            width = f"{stats['avg_width']} ± {stats['std_width']}"
            std = stats['std_center'] + stats['std_width']
            print(f"{method:<25} {center:<15} {width:<15} {std}")
    
    # Save comparison
    output_path = Path("../../vendors/Siemens/inbreast_method_comparison.json")
    import json
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Full comparison saved to: {output_path}")
    
    return results


def example_apply_windowing():
    """
    Example: Apply calculated windowing to an image.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Apply Windowing Transformation")
    print("=" * 70)
    
    # Load image
    inbreast_dir = Path("/home/eloygarcia/Escritorio/Datasets/inbreast/ALL-IMGS")
    sample_dcm = list(inbreast_dir.glob("*.dcm"))[0]
    
    dcm = pydicom.dcmread(sample_dcm)
    image = dcm.pixel_array
    
    print(f"Original image: {image.shape}, dtype: {image.dtype}")
    print(f"Value range: {image.min()} - {image.max()}")
    
    # Calculate windowing
    method = get_mammography_preset('breast_optimized')
    center, width = calculate_windowing(image, method=method)
    
    print(f"\nCalculated windowing:")
    print(f"  Center: {center}")
    print(f"  Width: {width}")
    
    # Apply windowing
    windowed = apply_windowing(
        image.copy(),
        window_center=center,
        window_width=width,
        voi_func='LINEAR',
        y_min=0,
        y_max=image.max(),
        backend='np_v2'
    )
    
    print(f"\nWindowed image: {windowed.shape}, dtype: {windowed.dtype}")
    print(f"Value range: {windowed.min()} - {windowed.max()}")
    
    # Visualize before/after
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Original
    axes[0].imshow(image, cmap='gray')
    axes[0].set_title('Original Image\n(16-bit, full range)', fontsize=12)
    axes[0].axis('off')
    
    # Windowed
    axes[1].imshow(windowed, cmap='gray', vmin=0, vmax=windowed.max())
    axes[1].set_title(f'Windowed Image\nCenter:{center} Width:{width}', fontsize=12)
    axes[1].axis('off')
    
    # Histogram comparison
    tissue = image[image > 0]
    axes[2].hist(tissue, bins=100, alpha=0.7, label='Original', color='blue')
    axes[2].axvline(center - width/2, color='red', linestyle='--', label='Window limits')
    axes[2].axvline(center + width/2, color='red', linestyle='--')
    axes[2].axvline(center, color='green', linestyle='-', linewidth=2, label='Window center')
    axes[2].set_xlabel('Pixel Value')
    axes[2].set_ylabel('Frequency')
    axes[2].set_title('Histogram & Window', fontsize=12)
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = Path("windowing_before_after.png")
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Visualization saved to: {output_path}")
    plt.close()
    
    return windowed


def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 70)
    print("MAMMOGRAPHY WINDOWING EXAMPLES")
    print("InBreast Dataset Analysis")
    print("=" * 70)
    
    # Check if dataset exists
    inbreast_dir = Path("/home/eloygarcia/Escritorio/Datasets/inbreast/ALL-IMGS")
    if not inbreast_dir.exists():
        print(f"\nError: InBreast dataset not found at {inbreast_dir}")
        print("Please update the path in the script.")
        return
    
    try:
        # Example 1: Single image
        print("\n🔍 Running Example 1: Single Image Analysis...")
        example_single_image()
        
        # Example 2: Dataset analysis
        print("\n🔍 Running Example 2: Dataset-wide Analysis...")
        example_dataset_analysis()
        
        # Example 3: Method comparison
        print("\n🔍 Running Example 3: Method Comparison...")
        example_method_comparison()
        
        # Example 4: Apply windowing
        print("\n🔍 Running Example 4: Apply Windowing...")
        example_apply_windowing()
        
        print("\n" + "=" * 70)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nGenerated files:")
        print("  - windowing_comparison.png")
        print("  - windowing_before_after.png")
        print("  - ../../vendors/Siemens/inbreast_windowing_statistics.json")
        print("  - ../../vendors/Siemens/inbreast_method_comparison.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
