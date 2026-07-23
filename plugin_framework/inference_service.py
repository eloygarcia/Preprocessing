import requests

"""
class InferenceService:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def predict(
        self,
        algorithm_name,
        image
    ):
        payload = {
            "image": image.tolist()
        }
        plugin = self.plugin_manager.get_algorithm(
            algorithm_name
        )
        response = requests.post(
            f"{plugin['url']}/predict",
            json=payload
        )
        return response.json()
"""
       
class InferenceRequest:
    def __init__(
        self,
        image,
        metadata=None
    ):
        self.image = image
        self.metadata = metadata

class InferenceService:
    def __init__(
        self,
        plugin_manager,
        algorithm_client
    ):
        self.plugin_manager = plugin_manager
        self.algorithm_client = algorithm_client

class AlgorithmClient:
    def predict(
        self,
        url,
        payload
    ):
        response = requests.post(
            f"{url}/predict",
            json=payload
        )
        return response.json()