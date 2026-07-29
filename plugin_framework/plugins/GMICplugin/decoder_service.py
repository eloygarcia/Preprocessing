import json
import base64
import uuid

from dataclasses import asdict
from pathlib import Path
import numpy as np
import nibabel as nib
import requests


class MammographyDecoder:        
    @staticmethod
    def decode(request: dict) -> np.ndarray:

        ## Decode the image from the request dictionary
        image_path = request["data_path"]

        if image_path is not None:
            image_path = Path(image_path)
            nii_file = nib.load(image_path)
            image_array = nii_file.get_fdata()
            
            if not image_path.exists():
                raise FileNotFoundError(f"Decoded image file not found at {image_path}")
        elif image_path is None:
            raise ValueError("Response JSON does not contain 'data_path' key.")

        ## Decocde the metadata from the request dictionary
        metadata = json.loads(request["metadata"])

        return image_array, metadata

class ResultsEncoder:
    @staticmethod
    def encode(results: dict) -> dict:
        encoded_results = {}
        for key, value in results.items():
            if isinstance(value, np.ndarray):
                # Convert numpy array to bytes and then encode to base64
                random_name = str(uuid.uuid4())
                ## guardamos temporal como archivo nii.gz
                image_path = Path("/tmp/", f"{random_name}.nii.gz")
                nib.save(nib.Nifti1Image(value, np.eye(4)), image_path)
                encoded_results[key] = str(image_path)
            else:
                encoded_results[key] = str(value)

        return json.dumps(encoded_results)