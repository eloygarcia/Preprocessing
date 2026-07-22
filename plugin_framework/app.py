from fastapi import FastAPI
from plugin_framework.predictor import Predictor

app = FastAPI()

@app.get("/health")
def health():
    return Predictor.health()


@app.get("/metadata")
def metadata():
    return Predictor.metadata()


@app.post("/predict")
def predict(request):
    return Predictor.predict(request)