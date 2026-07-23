import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

from .unet import Unet

import pickle
from functools import partial

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.num_classes = 2

        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)
        self.model_weight_path = dir_path+'/weights/segmentation_weights.ckpt'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = self.load_model()
        self.model.to(self.device)
        self.model.eval()

    def load_model(self):
        self.model = Unet.load_from_checkpoint(self.model_weight_path, 
                                                num_classes= 3,
                                                input_channels=1,
                                                depth=5,
                                                features_start=64,
                                                bilinear=True,
                                                map_location= self.device,
                                                weights_only=False,
                                                strict=False,
                                                pickle_module=pickle)

        """
        weights = torch.load(
            self.model_weight_path,
            map_location=self.device,
            weights_only = False
        )

        model.load_state_dict(weights)
        """
        return self.model
    
    def forward(self, x):
        return self.model(x)