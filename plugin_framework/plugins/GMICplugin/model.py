import os
import yaml
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

import pickle
from functools import partial

from src.modeling import gmic as gmic


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

        ## Configuration parameters
        self.config = {}
        with open("config.yaml") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        
        self.num_classes = self.config['parameters']['num_classes']

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.model_weight_path = os.path.join(dir_path,self.config['weights'])
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.config['device'] =  self.device

        self.model = self.load_model()
        self.model.to(self.device)
        self.model.eval()

    def get_configuration(self):
        return self.config

    def load_model(self):
        self.model = gmic.GMIC(self.config['parameters'])

        self.model.load_state_dict(torch.load(self.model_weight_path,
                                              map_location=self.device), 
                                   strict=False)

        """
        weights = torch.load(
            self.model_weight_path,
            map_location=self.device,
            weights_only = False
        )

        model.load_state_dict(weights)
        """
        return self.model

    def get_network(self):
        return self.model
    
    def forward(self, x):
        return self.model(x)