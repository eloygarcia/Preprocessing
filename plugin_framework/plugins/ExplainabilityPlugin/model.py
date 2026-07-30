import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.num_classes = 0
        
        self.weights_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_weight_path = ""

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model(self, model_name='efficientnetb0'):        
        if model_name == 'efficientnetb0':
            self.num_classes = 2
            self.model_weight_path = self.weights_dir + '/weights/best_model_efficientnetb0_full_1024_RSNA_OMIDB_crop.pth'

            model = torchvision.models.efficientnet_b0()
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, self.num_classes)
        elif model_name == 'resnet50':
            self.num_classes = 1
            self.model_weight_path = self.weights_dir + '/weights/best_model_resnet50_ft_full_1024.pth'

            model = torchvision.models.resnet50()
            for param in model.parameters():
                param.requires_grad = False
            model.fc = nn.Linear(model.fc.in_features, self.num_classes)
        else:
            raise ValueError(f"Unsupported model name: {model_name}")
        
        weights = torch.load(
            self.model_weight_path,
            map_location=self.device
        )

        model.load_state_dict(weights)
        
        return model

    def initialize_model(self, model_name='efficientnetb0'):
        self.model = self._load_model(model_name)
        self.model = self.model.to(self.device)
        self.model.eval()

    def forward(self, x):
        return self.model(x)