import numpy as np
from copy import deepcopy
from typing import Tuple, Dict, List, Optional
try:
    from .apply_windowing import _apply_windowing_np_v1, _apply_windowing_np_v2
except ImportError:
    from apply_windowing import _apply_windowing_np_v1, _apply_windowing_np_v2


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize the image to the range [0, 1].
    
    Args:
        image: 2D numpy array of pixel values
    
    Returns:
        Normalized image as a 2D numpy array
    """
    img = image.copy()
    img = img.astype(float)
    img_min = img.min()
    img_max = img.max()
    if img_max == img_min:
        return np.zeros_like(image)
    img = (img - img_min) / (img_max - img_min)
    return img.astype(image.dtype if isinstance(image, np.ndarray) else img.dtype)

"""
def ensure_monochrome2(
    image: np.ndarray,
    photometric_interpretation: str,
) -> np.ndarray:

    if photometric_interpretation != "MONOCHROME1":
        return image

    return image.max() - image
"""

def calculate_windowing(image: np.ndarray, 
                       method: str = 'breast_tissue',
                       exclude_background: bool = True) -> Tuple[int, int]:
    """
    Calculate optimal window center and width from image histogram.
    
    Args:
        image: 2D numpy array of pixel values
        method: Calculation method. Options:
            - 'percentile_1_99': Percentiles 1-99 (robust, general use)
            - 'percentile_2_98': Percentiles 2-98 (more conservative)
            - 'percentile_5_95': Percentiles 5-95 (tight, high contrast)
            - 'breast_tissue': Optimized for mammography breast tissue (25-95 percentile)
            - 'statistical': Mean ± 2 standard deviations
            - 'statistical_wide': Mean ± 3 standard deviations
            - 'full_range': Complete value range (min-max)
            - 'histogram_peak': Based on histogram mode and FWHM
        exclude_background: If True, exclude zero pixels (background)
    
    Returns:
        Tuple of (window_center, window_width) as integers
    """
    # Filter background if requested
    if exclude_background:
        tissue_pixels = image[image > 0]
        if len(tissue_pixels) == 0:
            raise ValueError("No non-zero pixels found in image")
    else:
        tissue_pixels = image.flatten()
    
    # Calculate based on method
    if method == 'percentile_1_99':
        p1, p99 = np.percentile(tissue_pixels, [1, 99])
        center = (p1 + p99) / 2
        width = p99 - p1
        
    elif method == 'percentile_2_98':
        p2, p98 = np.percentile(tissue_pixels, [2, 98])
        center = (p2 + p98) / 2
        width = p98 - p2
        
    elif method == 'percentile_5_95':
        p5, p95 = np.percentile(tissue_pixels, [5, 95])
        center = (p5 + p95) / 2
        width = p95 - p5
        
    elif method == 'breast_tissue':
        # Optimized for mammography: focus on glandular tissue
        # Lower percentile to include fatty tissue, higher for dense tissue
        p25, p95 = np.percentile(tissue_pixels, [25, 95])
        center = (p25 + p95) / 2
        width = (p95 - p25) * 1.5  # Expand slightly for better visualization
        
    elif method == 'statistical':
        mean = np.mean(tissue_pixels)
        std = np.std(tissue_pixels)
        center = mean
        width = 4 * std  # ±2 standard deviations
        
    elif method == 'statistical_wide':
        mean = np.mean(tissue_pixels)
        std = np.std(tissue_pixels)
        center = mean
        width = 6 * std  # ±3 standard deviations
        
    elif method == 'full_range':
        min_val = np.min(tissue_pixels)
        max_val = np.max(tissue_pixels)
        center = (min_val + max_val) / 2
        width = max_val - min_val
        
    elif method == 'histogram_peak':
        # Calculate histogram
        hist, bins = np.histogram(tissue_pixels, bins=256)
        
        # Find peak (mode)
        peak_idx = np.argmax(hist)
        peak_value = bins[peak_idx]
        center = peak_value
        
        # Find Full Width at Half Maximum (FWHM)
        half_max = hist[peak_idx] / 2
        
        # Find left side of FWHM
        left_idx = peak_idx
        while left_idx > 0 and hist[left_idx] > half_max:
            left_idx -= 1
        
        # Find right side of FWHM
        right_idx = peak_idx
        while right_idx < len(hist) - 1 and hist[right_idx] > half_max:
            right_idx += 1
        
        # Calculate width from FWHM
        left_value = bins[left_idx]
        right_value = bins[right_idx]
        width = (right_value - left_value) * 1.75 # Expand beyond FWHM
        
        # Ensure reasonable width
        if width < 100:
            width = 4 * np.std(tissue_pixels)
    
    else:
        raise ValueError(
            f"Unknown method '{method}'. Valid options: "
            "'percentile_1_99', 'percentile_2_98', 'percentile_5_95', "
            "'breast_tissue', 'statistical', 'statistical_wide', "
            "'full_range', 'histogram_peak'"
        )
    
    return int(center), int(width)


def apply_windowing(arr,
                    window_width=None,
                    window_center=None,
                    voi_func='LINEAR',
                    y_min=0,
                    y_max=255,
                    backend='np_v2'):
    
    #if backend == 'torch':
    #    if isinstance(arr, torch.Tensor):
    #        pass
    #    elif isinstance(arr, np.ndarray):
    #        if arr.dtype == np.uint16:
    #            arr = torch.from_numpy(arr, torch.int16)
    #        else:
    #            arr = torch.from_numpy(arr)

    if backend == 'np_v1':
        windowing_func = _apply_windowing_np_v1
    elif backend == 'np_v2':
        windowing_func = _apply_windowing_np_v2
    # elif backend == 'torch':
    #    windowing_func = _apply_windowing_torch
    else:
        raise ValueError(
            f'Invalid backend {backend}, must be one of ["np_v1", "np_v2", "torch"]'
        )

    arr_windowed = windowing_func(arr,
                         window_width=window_width,
                         window_center=window_center,
                         voi_func=voi_func,
                         y_min=y_min,
                         y_max=y_max)
    
    ### To fit the initial image range, we can normalize the windowed image to the original range
    # arr_windowed = arr.max() * (arr_windowed- arr_windowed.min()) / (arr_windowed.max() - arr_windowed.min())
    
    #return arr_windowed.astype( arr.dtype if isinstance(arr, np.ndarray) else arr_windowed.dtype)
    return arr_windowed
