from fastapi import FastAPI
from predictor import Predictor

app = FastAPI()

@app.get("/health")
def health():
    return Predictor().health_check()


@app.get("/metadata")
def metadata():
    return Predictor().get_metadata()


@app.post("/predict")
def predict(request):
    return Predictor().predict(request)