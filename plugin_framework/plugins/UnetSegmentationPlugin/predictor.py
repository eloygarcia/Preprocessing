import os
import json
import numpy as np
import torch
from abc import ABC, abstractmethod

from decoder_service import MammographyDecoder, ResultsEncoder

from model import Model
from preprocessing import Preprocessing
from postprocessing import Postprocessing

from skimage.transform import resize

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

        self.decoder = MammographyDecoder()
        self.encoder = ResultsEncoder()
    
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
            "device": str(self.device)
        }
    
    def get_metadata(self):
        return self.metadata
    
    @torch.no_grad()
    def predict(self, request):
        image, metadata = self.decoder.decode(request)

        x = self.preprocess(image,metadata).to(self.device)    
        y = self.model(x)
        mask = self.postprocess(y, metadata)

        encoded_results = self.encoder.encode({
                    "segmentation_mask": mask
                })
        
        return encoded_results
    