import os
import json
import torch
from abc import ABC, abstractmethod

from model import Model
from preprocessing import Preprocessing
from postprocessing import Postprocessing

class Predictor(ABC):
    """
    Base predictor for all MammoLab AI plugins.

    The predictor is responsible for:

    - Loading the model
    - Performing preprocessing
    - Running inference
    - Performing postprocessing
    """
    def __init__(
        self,
        device=None
    ):
        metadata_path = os.path.dirname(os.path.realpath(__file__)) + '/plugin.json'
        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)
        
        self.device = device or self._select_device()
        
        self.model = Model()
        self.model = self.model.to(self.device)
        self.model.eval()
    
        self.preprocess = Preprocessing
        self.postprocess = Postprocessing
    
    def _select_device(self):
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")
    
    def _warm_up(self):
        pass

    def get_device(self):
        return self.device
    
    def health_check(self):
        return {
            "status": "ok",
            "model_loaded":True,
            "device":self.device
        }
    
    def get_metadata(self):
        return self.metadata
    
    def get_configuration(self):
        return self.model.get_configuration()
        
    
    @torch.no_grad()
    def predict(self, data):
        x = self.preprocess(data).to(self.device)    
        y = self.model(x)
        probs = self.postprocess(y)

        saliency_map = self.model.get_network().saliency_map.data.cpu().numpy()[0,1,:,:]
        
        return probs, saliency_map
    