import os
import json
import torch
from abc import ABC, abstractmethod
#from plugin_framework.predictor import Predictor

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

    def __init__(self):
        pass
        # with open(metadata_path, "r") as f:
        #     self.metadata = json.load(f)
        
    def _select_device(self):
        pass
    
    def _get_device(self):
        pass

    def _warmup(self):
        pass

    def health_check(self):
        return {"status": "ok"} 

    def get_metadata(self):
        pass
    
    @torch.no_grad()
    def predict(self, data):
       pass

# class Predictor(ABC):
class ResNetPredictor(Predictor):
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

    def get_device(self):
        return self.device
    
    def health_check(self):
        return {"status": "ok"}
    
    def get_metadata(self):
        return self.metadata
    
    @torch.no_grad()
    def predict(self, data):
        print(self.device)

        #self.model = self.model.to(self.device)
        #self.model.eval()
        
        x = self.preprocess(data).to(self.device)    

        y = self.model(x)
        probs = self.postprocess(y)
        
        # return y.float().cpu().numpy()
        return probs.cpu()
    