from fastapi import FastAPI
from predictor import ResNetPredictor

app = FastAPI()
predictor = ResNetPredictor()

@app.get("/health")
def health():
    return predictor.health_check()

@app.get("/metadata")
def metadata():
    return predictor.get_metadata()


@app.post("/predict")
def predict(request):
    return predictor.predict(request)

"""
# app.py

plugins = PluginManager()

plugins.load("lesion_detector")

plugin = plugins.get("lesion_detector")

result = plugin.analyse(image)

viewer.display(result)
"""