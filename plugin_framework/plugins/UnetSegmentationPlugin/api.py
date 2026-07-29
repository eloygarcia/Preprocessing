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
    return predictor.predict(request)