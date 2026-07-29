import numpy as np
from fastapi import FastAPI, Body
from predictor import Predictor
from pydantic import BaseModel

from decoder_service import MammographyDecoder, ResultsEncoder

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

    decoder = MammographyDecoder()
    image, metadata = decoder.decode(request)

    score, saliency_map = predictor.predict(image, metadata)

    encoder = ResultsEncoder()
    encoded_results = encoder.encode({
        "score": score,
        "saliency_map": saliency_map
    })

    return encoded_results