import numpy as np
from copy import deepcopy

try:
    from ..processing.photometric import apply_windowing, normalize_image, calculate_windowing
except ImportError:
    try:
        from api_stable.processing.photometric import apply_windowing, normalize_image, calculate_windowing
    except ImportError:
        from processing.photometric import apply_windowing, normalize_image, calculate_windowing

class MammographyImage:
    """
    A class representing a mammography image.
    
    Properties:
    - shape
    - dtype
    - min
    - max

    # 1. Conversion fotometrica MONOCHROME 1 TO MONOCHROME 2
    # 2. windowing
    # 3. Normalization
    # 4. Crop Breast
    # 5. Resize
    # 6. Image history : 
    # return transformations: ex. [
    #    "ensure_monochrome2",
    #    "apply_window",
    #    "normalize"
    #]
    """
    def __init__(self, pixel_array):
        self._pixel_array = pixel_array
        self.history = []
        self.last_windowing = None

    @property
    def pixel_array(self):
        return self._pixel_array
    
    @property
    def shape(self):
        return self._pixel_array.shape  
    
    @property
    def dtype(self):
        return self._pixel_array.dtype  
    
    @property
    def min(self):
        return self._pixel_array.min() 
    
    @property
    def max(self):
        return self._pixel_array.max()  
    
    def copy(self):
        return deepcopy(self)

    def to_numpy(self):
        return self._pixel_array
    
    def get_history(self):
        return self.history

    def normalize(self):
        ## Normalize the image to the range [0,1]
        self._pixel_array = normalize_image(self._pixel_array)
        
        ## Update history of transformations
        self.history.append("normalize")
        return self

    def convert_to_monochrome2(self):
        ## Convert MONOCHROME1 to MONOCHROME2
        self._pixel_array = self.max - self._pixel_array

        ## Update history of transformations
        self.history.append(
            "convert_to_monochrome2"
        )
        return self
        
    def apply_windowing(
        self,
        window_center=None,
        window_width=None,
        voi_lut_function=None,
        backend="np_v2",
    ):

        """
        print(isinstance(window_center, (list,tuple)))
        print(isinstance(window_width, (list,tuple)))
        
        if isinstance(window_center, (list,tuple)) and len(window_center)>0:
            # Example explanation values: NORMAL, HARDER, SOFTER
            center = window_center[0]
            width = window_width[0]
        elif isinstance(window_width, (list,tuple)) and len(window_width)>0:
            # Example explanation values: NORMAL, HARDER, SOFTER
            center = window_center
            width = window_width[0]
        """

        voi_func = "LINEAR"
        if voi_lut_function is not None and str(voi_lut_function).upper() == "SIGMOID":
            voi_func = "SIGMOID"


        # if window_center is None and window_width is None and
        if voi_lut_function=="LINEAR":
            center = (self.max + self.min) / 2
            width = (self.max - self.min)
        elif window_center is None or window_width is None and voi_lut_function=="SIGMOID":
            center, width = calculate_windowing(self._pixel_array)
        else:
            center = window_center
            width = window_width
        
        ## Performing windowing
        self._pixel_array = apply_windowing(
            self._pixel_array,
            window_center = center,
            window_width = width,
            voi_func = voi_func,
            y_min = self.min,
            y_max = self.max,
            backend = backend,
        )

        ## Ensure the pixel values are in the same range as the original image
        current_max = self.max
        self._pixel_array = current_max * normalize_image(self._pixel_array)
        self.last_windowing = {
            "window_center": center,
            "window_width": width,
            "voi_lut_function": voi_func,
        }
        
        ## History of transformations
        self.history.append(
            f"apply_windowing( window_center={center}, window_width={width}, voi_lut_function={voi_func})"
        )
        return self
    

    
    


