import cv2
import numpy as np
import torch

def Postprocessing(prediction):
    # Implement your postprocessing logic here
    # For example, you can convert the prediction to a specific format or apply any necessary transformations
    # return torch.sigmoid(prediction)
    return prediction.argmax(dim=1).squeeze(0)

def _extend_mask_upward_and_sideways(mask, bbox_coords):
    """
    Extend the pectoral muscle mask (value 2) upward and toward the nearest lateral side.
    
    Parameters:
    -----------
    mask : np.ndarray
        The segmentation mask
    bbox_coords : tuple
        Bounding box coordinates (x_min, y_min, x_max, y_max)
    
    Returns:
    --------
    np.ndarray
        Extended mask
    """
    x_min, y_min, x_max, y_max = bbox_coords
    
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
            
            # Fill from most interior pixel to the nearest lateral edge
            if dist_to_left <= dist_to_right:
                # Left edge is closer, fill from left edge to interior pixel
                extended_mask[row, x_min:most_interior_col + 1] = 2
            else:
                # Right edge is closer, fill from interior pixel to right edge
                extended_mask[row, most_interior_col:x_max] = 2
    
    # Apply morphological closing to fill holes in the pectoral muscle mask
    pectoral_region_extended = (extended_mask == 2).astype(np.uint8)
    
    # Define a kernel for closing
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
    
    # Apply closing operation
    closed_pectoral = cv2.morphologyEx(pectoral_region_extended, cv2.MORPH_CLOSE, kernel)
    
    # Update the extended mask with the closed pectoral region
    extended_mask[closed_pectoral == 1] = 2
    
    return extended_mask


def _get_segmentation_probabilities(self, input_image, output_size=None):
    """
        Gives a segmentation probabilities back for an input image
        input_image: can be a path to dicom mammogram or a numpy array (ideally with pixel spacing 0.4 mm)
        output_size: if specified, the model will return the segmentation in output size, if None, the output will
        match the original size of the mammogram. Default is None
    """
    image, original_size = self._check_and_get_correct_image_input(input_image)
    image = image.to(self.model.device)  # put image to same device as model

    # run_model
    output = self.model.eval().forward(image.unsqueeze(0).unsqueeze(0), pad_tensor=True)

    # upsample to original size
    if output_size:
        output = torch.nn.functional.interpolate(output, size=output_size, mode='bilinear', align_corners=False)
    else:
        output = torch.nn.functional.interpolate(output, size=original_size, mode='bilinear', align_corners=False)
    return output

def _get_segmentation(self, input_image, fill_holes_in_breast=False, output_size=None):
    """
        Gives a segmentation back for an input image
        input_image: can be a tensor or a path to a path to dicom image
        fill_holes_in_breast: if True, this function will only keep the largest segmented breast area and fill any
        existing holes
        output_size: if specified, the model will return the segmentation in output size, if None, the output will
        match the original size of the mammogram. Default is None
        :return:
    """
    output = self.get_segmentation_probabilities(input_image, output_size)
    
    # get segmentation
    segmentation = output.argmax(dim=1)
    # segmentation = output[:,2,:,:] 
    segmentation = segmentation.squeeze().to('cpu').numpy()
    if fill_holes_in_breast:
        print("Filling holes in breast segmentation...")
        segmentation = self._fill_holes_in_breast(segmentation)
    return segmentation