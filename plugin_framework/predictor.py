from abc import ABC, abstractmethod

import torch


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
        self.device = self._select_device()
        self.model = self.load_model()
        self.model.to(self.device)
        self.model.eval()
        self._warmup()

    @torch.no_grad()
    def predict(self, data):
        x = self.preprocess(data)
        x = x.to(self.device)
        y = self.model(x)
        result = self.postprocess(y)
        return result

    def _select_device(self):
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def _warmup(self):
        pass

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def preprocess(self, data):
        pass

    @abstractmethod
    def postprocess(self, prediction):
        pass

    def health(self):
        return {"status": "ok"} 

    def metadata(self):
        return {
            "name": self.__class__.__name__,
            "description": self.__doc__,
        }