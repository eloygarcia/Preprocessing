import json

import base64
from dataclasses import asdict
from pathlib import Path
import numpy as np
import nibabel as nib
import requests



class MammographyDecoder:        
    @staticmethod
    def decode(response):
        response_json = response.json()
        image_path = response_json.get("data_path")
        if image_path is not None:
            image_path = Path(image_path)
            nii_file = nib.load(image_path)
            image_array = nii_file.get_fdata()
            
            if not image_path.exists():
                raise FileNotFoundError(f"Decoded image file not found at {image_path}")
        elif image_path is None:
            raise ValueError("Response JSON does not contain 'data_path' key.")
        # metadata = response_json.get("metadata")
        return image_array