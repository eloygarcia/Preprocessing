from fastapi import FastAPI
from predictor import UnetPredictor

app = FastAPI()
predictor = UnetPredictor()

@app.get("/health")
def health():
    return predictor.health_check()


@app.get("/metadata")
def metadata():
    return predictor.get_metadata()


@app.post("/predict")
def predict(request):
    return predictor.predict(request)