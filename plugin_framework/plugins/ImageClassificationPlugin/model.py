import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.num_classes = 2
        #self.model_weight_path = './weights/best_model_resnet50_ft_full_1024.pth'
        
        weights_dir = os.path.dirname(os.path.realpath(__file__))
        self.model_weight_path = weights_dir + '/weights/best_model_efficientnetb0_full_1024_RSNA_OMIDB_crop.pth'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = self.load_model()
        self.model.to(self.device)
        self.model.eval()

    def load_model(self):        
        """
        #weights = torchvision.models.ResNet50_Weights.DEFAULT
        model = torchvision.models.resnet50()
    
        for param in model.parameters():
            param.requires_grad = False
        model.fc = nn.Linear(model.fc.in_features, self.num_classes)
        """
        model = torchvision.models.efficientnet_b0()
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, self.num_classes)
        
        weights = torch.load(
            self.model_weight_path,
            map_location=self.device
        )

        model.load_state_dict(weights)
        
        return model
    
    def forward(self, x):
        return self.model(x)