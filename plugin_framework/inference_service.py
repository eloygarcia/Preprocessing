import requests

from plugin_manager import PluginManager
from encoder_service import MammographyEncoder

from api_stable.mammography import MammographyDicom


class InferenceService:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.encoder = MammographyEncoder()

    def _check_status(self, plugin):
        health = requests.get(
            f"{plugin.get_url()}/health")
        print(health.json())

        if health.json()['status'] != 'ok':
            raise RuntimeError("Health check failed")

    def predict(
        self,
        algorithm_name: str,
        image: MammographyDicom
    ):
        ## 1. Get the plugin for the specified algorithm
        plugin = self.plugin_manager.get_algorithm(
            algorithm_name
        )

        ## 2. Check the health status of the plugin before making the prediction request
        self._check_status(plugin)

        ## 3. Encode the image and metadata into a payload for the plugin
        payload = self.encoder.encode(image)

        ## 4. Make the prediction request to the plugin's /predict endpoint
        response = requests.post(
            f"{plugin.get_url()}/predict",
            json=payload
        )
        
        return response #.json()

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
"""