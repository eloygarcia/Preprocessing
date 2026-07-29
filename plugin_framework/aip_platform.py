
from plugin_manager import PluginManager
from inference_service import InferenceService
from encoder_service import MammographyEncoder

from api_stable.mammography import MammographyDicom



class AIPlatform:
    def __init__(self):

        self.manager = PluginManager()
        self.manager.discover()
        
        self.service = InferenceService(self.manager)

        self.results = {}
        
    def predict(
        self,
        algorithm,
        image
    ):
        self.results['algorithm'] = algorithm
        self.results['version'] = self.manager.get_algorithm(algorithm).get_metadata()['version']
        self.results['task'] = self.manager.get_algorithm(algorithm).get_metadata()['info']['task']
        
        self.results['results'] = self.service.predict(
            algorithm,
            image).json()

        return self.results