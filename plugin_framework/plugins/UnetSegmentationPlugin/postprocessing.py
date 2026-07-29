import cv2
import numpy as np
import torch

from skimage.transform import resize

def Postprocessing(prediction, metadata):
    # Implement your postprocessing logic here
    # For example, you can convert the prediction to a specific format or apply any necessary transformations
    # upsample to original size
    output_size = [metadata['rows'], metadata['columns']]
    prediction = torch.nn.functional.interpolate(prediction, size=output_size, mode='bilinear', align_corners=False)
    mask =prediction.argmax(dim=1).squeeze(0)
    
    if metadata['laterality'] == "R":
        mask = np.fliplr(mask.cpu().numpy())
    else:
        mask = mask.cpu().numpy()
    """
    if metadata['view'] == "CC":
        mask[mask == 2] = 1
    elif metadata['view'] == "MLO":
        # Extend the pectoral muscle mask (value 2) upward and toward the nearest lateral side
        # Get bounding box coordinates for the pectoral muscle region
        pectoral_mask = (mask == 2).astype(np.uint8)
        contours, _ = cv2.findContours(pectoral_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the largest contour (assuming it's the pectoral muscle)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Extend the pectoral muscle mask
            # mask = _extend_mask_upward_and_sideways(mask)
        else:
            print("Warning: No pectoral muscle found in the segmentation mask.")
    """        
    return mask.astype(np.uint8)

def _extend_mask_upward_and_sideways(mask):
    """
    Extend the pectoral muscle mask (value 2) upward and toward the nearest lateral side.
    Only works for Left images!! 
    
    Parameters:
    -----------
    mask : np.ndarray
        The segmentation mask    
    Returns:
    --------
    np.ndarray
        Extended mask
    """    
    # Validate and clip bounding box coordinates to image dimensions
    height, width = mask.shape[:2]
    x_min = max(0, min(x_min, width - 1))
    x_max = max(0, min(x_max, width))
    y_min = max(0, min(y_min, height - 1))
    y_max = max(0, min(y_max, height))
    
    # Ensure valid range
    if x_min >= x_max or y_min >= y_max:
        print(f"  ⚠️  Warning: Invalid bounding box after clipping: ({x_min}, {y_min}, {x_max}, {y_max})")
        return mask.copy()
    
    extended_mask = mask.copy()
    
    # Extract pectoral muscle region (value 2)
    pectoral_mask = (mask == 2).astype(np.uint8)
    
    if pectoral_mask.sum() == 0:  # No pectoral muscle found
        return extended_mask
    
    # Get pectoral region within bounding box
    pectoral_region = pectoral_mask[y_min:y_max, x_min:x_max]
    
    if pectoral_region.sum() == 0:
        return extended_mask
    
    # EXTEND UPWARD: For each column, find topmost pectoral pixel and fill upward
    for col in range(x_min, x_max):
        col_pectoral = pectoral_mask[y_min:y_max, col]
        pectoral_rows = np.where(col_pectoral > 0)[0]
        
        if len(pectoral_rows) > 0:
            topmost_pectoral = pectoral_rows[0] + y_min
            # Fill from top of image to topmost_pectoral with value 2
            extended_mask[0:topmost_pectoral, col] = 2
    
    # EXTEND SIDEWAYS: For each row, find the pectoral pixel closest to center
    # and fill from that pixel to the nearest lateral edge
    bbox_center_x = mask.shape[1] / 2.0
    
    for row in range(0, y_max):
        row_pectoral = extended_mask[row, x_min:x_max]
        pectoral_cols = np.where(row_pectoral == 2)[0]

        if len(pectoral_cols) > 0:
            # Convert to full image coordinates
            pectoral_cols_full = pectoral_cols + x_min
            
            # Find the pectoral pixel closest to center (most interior)
            distances_to_center = np.abs(pectoral_cols_full - bbox_center_x)
            most_interior_idx = np.argmin(distances_to_center)
            most_interior_col = pectoral_cols_full[most_interior_idx]
            
            # Determine which lateral edge is closer to the most interior pixel
            dist_to_left = abs(most_interior_col - 0)
            dist_to_right = abs(most_interior_col - mask.shape[1])
            
            
            extended_mask[row, x_min:most_interior_col + 1] = 2
            
    # Apply morphological closing to fill holes in the pectoral muscle mask
    pectoral_region_extended = (extended_mask == 2).astype(np.uint8)
    
    # Define a kernel for closing
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
    
    # Apply closing operation
    closed_pectoral = cv2.morphologyEx(pectoral_region_extended, cv2.MORPH_CLOSE, kernel)
    
    # Update the extended mask with the closed pectoral region
    extended_mask[closed_pectoral == 1] = 2
    
    return extended_mask
