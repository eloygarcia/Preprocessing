from fastapi import FastAPI
from inference_service import InferenceService
from plugin_framework import PluginManager

app = FastAPI()
plugin_manager = PluginManager()

service = InferenceService(plugin_manager=plugin_manager)

@app.post("/predict")
def predict(request):
    result = service.predict(
        request.algorithm,
        request.data
    )

    return result