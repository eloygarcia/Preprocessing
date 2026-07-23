import numpy as np
from fastapi import FastAPI, Body
from predictor import ResNetPredictor
from pydantic import BaseModel

app = FastAPI()
predictor = ResNetPredictor()

class PredictionRequest(BaseModel):
    image: list

@app.get("/health")
def health():
    return predictor.health_check()

@app.get("/metadata")
def metadata():
    return predictor.get_metadata()

@app.post("/predict")
def predict(request: dict = Body(...)):
    image = np.array(
        request["image"]
    )
    print(image.shape)
    
    return predictor.predict(image)
    
    #return {
    #    "shape": list(image.shape)
    #}

# @app.post("/predict")
# def predict(request: PredictionRequest):
#    return predictor.predict(request.image)

