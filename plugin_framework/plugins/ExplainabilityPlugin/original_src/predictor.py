import numpy as np
from MultiModel import MultiModel
from Arguments import arguments

import torch
from torch.utils.data import DataLoader
from abc import ABC, abstractmethod

class BaseClassifier:
    def predict(
        self,
        image: np.ndarray,
    ):
        pass

# predictor.py
class BasePredictor(ABC):
    @abstractmethod
    def predict(self, image):
        pass

class Predictor:
    def __init__(
        self,
        model_path: str,
        architecture: str,
    ):
        self.model_path = model_path
        self.architecture = architecture
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiModel(args=arguments())
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def load_network(self):
        self.model = MultiModel(args=arguments())
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, dataloader: DataLoader):
        all_predictions = []
        with torch.no_grad():
            for batch in dataloader:
                inputs = batch.to(self.device)
                outputs = self.model(inputs)
                predictions = torch.argmax(outputs, dim=1)
                all_predictions.append(predictions.cpu().numpy())
        return np.concatenate(all_predictions)
