import base64
from dataclasses import asdict
from pathlib import Path
import numpy as np
import nibabel as nib
import requests

from api_stable.mammography import MammographyDicom

class ImageEncoder:
    @staticmethod
    def encode(image: MammographyDicom):
        # extraemos la imagen
        image_array = image.image.to_numpy()

        ## guardamos temporal como archivo nii.gz
        image_path = Path("./tmp", f"{image.get_internal_uid()}.nii.gz")
        print(image_path)
        try:
            image_path.parent.mkdir(parents=True, exist_ok=True)
            nib.save(nib.Nifti1Image(image_array, np.eye(4)), image_path)
        except Exception as e:
            print(f"Error creating directory {image_path.parent}: {e}")
            raise
        

        return {
            "data_path": image_path,
            "metadata": asdict(image.metadata) if image.metadata else None
        }

class ImageDecoder:
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
        metadata = response_json.get("metadata")
        return {
            "data_path": image_path,
            "metadata": metadata,
            "image_array": image_array
        }