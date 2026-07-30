import os
import json

import yaml
import torch
from abc import ABC, abstractmethod

from model import Model
from preprocessing import Preprocessing
from postprocessing import Postprocessing

from decoder_service import MammographyDecoder, ResultsEncoder

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

        self.config = {}
        with open("config.yaml") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        
        self.model_name = self.config['model']
        self.model = self._load_model()
    
        self.preprocess = Preprocessing
        self.postprocess = Postprocessing

        self.decoder = MammographyDecoder()
        self.encoder = ResultsEncoder()
    
    
    def _select_device(self):
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def get_device(self):
        return self.device
    
    def health_check(self):
        return {
            "status": "ok",
            "model_name": self.model_name,
            "model_loaded":True,
            "device": str(self.device)
        }
    
    def get_metadata(self):
        return self.metadata

    def _load_model(self):
        model = Model()
        model.initialize_model(self.model_name)
        return model
    
    
    @torch.no_grad()
    def predict(self, request: dict):
        ## Decode the request to get the image and metadata
        image, metadata = self.decoder.decode(request)

        ## Preprocess the image and run inference
        x = self.preprocess(image, metadata, self.config).to(self.device)
        y = self.model(x)
        probs = self.postprocess(y)

        ## Encode the results to return a JSON response
        encoded_results = self.encoder.encode({
            "score": str(probs),
            "heatmap": None
        })

        return encoded_results
    