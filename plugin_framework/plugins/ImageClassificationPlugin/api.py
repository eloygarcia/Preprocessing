from fastapi import FastAPI
from predictor import Predictor

app = FastAPI()
predictor = Predictor()

@app.get("/health")
def health():
    return Predictor().health_check()


@app.get("/metadata")
def metadata():
    return Predictor().get_metadata()


@app.post("/predict")
def predict(request):
    return Predictor().predict(request)

"""
# app.py

plugins = PluginManager()

plugins.load("lesion_detector")

plugin = plugins.get("lesion_detector")

result = plugin.analyse(image)

viewer.display(result)
"""