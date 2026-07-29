import os
import json

import base64
from dataclasses import asdict
from pathlib import Path
import numpy as np
import nibabel as nib
import requests

from api_stable.mammography import MammographyDicom

class MammographyEncoder:
    @staticmethod
    def encode(image: MammographyDicom):
        # extraemos la imagen
        image_array = image.image.to_numpy()
        
        ## guardamos temporal como archivo nii.gz
        image_path = Path("/tmp/", f"{image.get_internal_uid()}.nii.gz")

        try:
            image_path.parent.mkdir(parents=True, exist_ok=True)
            if not image_path.exists():
                nib.save(nib.Nifti1Image(image_array, np.eye(4)), image_path)
        except Exception as e:
            print(f"Error creating directory {image_path.parent}: {e}")
            raise
        
        ## metadata
        metadata = {}
        for k, v in dict(image.metadata).items():
            metadata.update(dict(v))

        return {
            "data_path":str(image_path),
            "metadata": json.dumps(metadata) if image.metadata else None
        }

class ResultsDecoder:        
    @staticmethod
    def decode(request: dict) -> np.ndarray:
        ## Decocde the metadata from the request dictionary
        metadata = request["results"]
        
        for key, value in metadata.items():
            if isinstance(value, str) and value.endswith('.nii.gz'):
                image_path = Path(value)
                if not image_path.exists():
                    raise FileNotFoundError(f"Decoded image file not found at {image_path}")
                nii_file = nib.load(image_path)
                image_array = nii_file.get_fdata()
                #request[key] = image_array

        
        return request, image_array
