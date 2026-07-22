import os
import json
import torch
from abc import ABC, abstractmethod

class Predictor(ABC):
    """
    Base predictor for all MammoLab AI plugins.

    The predictor is responsible for:

    - Loading the model
    - Performing preprocessing
    - Running inference
    - Performing postprocessing
    """

    def __init__(self, metadata_path):
        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)
        
    def _select_device(self):
        pass

    def _warmup(self):
        pass

    def health(self):
        return {"status": "ok"} 

    def metadata(self):
        pass
    
    @torch.no_grad()
    def predict(self, data):
       pass
