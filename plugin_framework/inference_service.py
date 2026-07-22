import requests

class InferenceService:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def predict(self,
                algorithm_name,
                data):
        algo = self.plugin_manager.get_algorithm(
            algorithm_name
        )
        print(algo)
        response = requests.post(
            f"{algo['url']}/predict",
            json=data
        )

        return response.json()