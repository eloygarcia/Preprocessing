import numpy as np
import cv2
import nibabel as nib

from fastapi import FastAPI, Body
from fastapi.responses import FileResponse
from predictor import Predictor
from pydantic import BaseModel

app = FastAPI()
predictor = Predictor()

class PredictionRequest(BaseModel):
    image: list

@app.get("/health")
def health():
    return predictor.health_check()

@app.get("/metadata")
def metadata():
    return predictor.get_metadata()

@app.get("/configuration")
def configuration():
    return predictor.get_configuration()

@app.post("/predict")
def predict(request: dict = Body(...)):
    image = np.array(
        request["image"], dtype=np.uint8
    )
    print(image.shape)
    print(type(image))

    mask = predictor.predict(image).astype(np.uint8)
    affine = np.eye(4)  # Create an identity affine matrix with the appropriate shape
    nifti_img = nib.Nifti1Image(mask, affine) 
                                
    #cv2.imwrite(
    #    "/tmp/mask.png",
    #    # "path": "/shared/results/mask.nii.gz"
    #    mask
    #    )

    nib.save(nifti_img, "/tmp/mask.nii.gz")
    
    #return FileResponse(
    #    "/tmp/mask.png",
    #    media_type="image/png",
    #    filename="mask.png"
    # )

    return { 
        "type": "mask",
        "data_path":"/tmp/mask.nii.gz",
        "shape": list(mask.shape),
        "dtype": str(mask.dtype)
    }