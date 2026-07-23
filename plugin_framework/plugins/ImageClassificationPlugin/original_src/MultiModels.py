import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

class MultiModel(nn.Module):
    def __init__(self, args):
        super(MultiModel, self).__init__()

        self.model_name = args.model
        self.pretrained = args.pretrained
        self.num_classes = args.num_classes
        self.weights_path = args.weights_path
        self.device = args.device

        match self.model_name:
            case 'resnet50':
                self.model = make_resnet50(args)
            case 'resnet50_ft':
                self.model = make_resnet50_ft(args)
            case 'resnet18_ft':
                self.model = make_resnet18_ft(args)
            case 'vgg16':
                self.model = make_vgg16(args)
            case 'vgg16_ft':
                self.model = make_vgg16_ft(args)
            case 'mobilenetv2':
                self.model = make_mobilenetv2(args)
            case 'inceptionv3':
                self.model = make_inceptionv3(args)
            case 'efficientnetb0':
                self.model = make_efficientnetb0(args)
            case 'efficientnetb3':
                self.model = make_efficientnetb3(args)
            case 'convnextsmall':
                self.model = make_convnextsmall(args)
            case 'convnextsmall_ft':
                self.model = make_convnextsmall_ft(args)
            case _:
                raise ValueError(f"Model {self.model_name} not recognized.")
    
    def forward(self,x):
        # return F.sigmoid(self.model(x))
        return self.model(x)


#### RESNET50
def make_resnet50(args):
    weights = torchvision.models.ResNet50_Weights.DEFAULT
    model = torchvision.models.resnet50(weights=weights)
    model.name = args.model
    
    for param in model.parameters():
        param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, args.num_classes)
    
    return model

#### RESNET50 FT
def make_resnet50_ft(args):
    weights = torchvision.models.ResNet50_Weights.DEFAULT
    model = torchvision.models.resnet50(weights=weights)
    model.name = args.model

    for name, param in model.named_parameters():
        if "layer4" not in name and "fc" not in name:
            param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, args.num_classes)
    
    return model

#### RESNET18 FT
def make_resnet18_ft(args):
    weights = torchvision.models.ResNet18_Weights.DEFAULT
    model = torchvision.models.resnet18(weights=weights)
    model.name = args.model

    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(model.fc.in_features, args.num_classes)
        )

    return model

#### VGG16
def make_vgg16(args):
    weights = torchvision.models.VGG16_Weights.DEFAULT
    model = torchvision.models.vgg16(weights=weights)
    model.name = args.model

    for param in model.parameters():
        param.requires_grad = False
    model.classifier[6] = torch.nn.Linear(4096, args.num_classes)
    
    return model

#### VGG16 FT
def make_vgg16_ft(args):
    weights = torchvision.models.VGG16_Weights.DEFAULT
    model = torchvision.models.vgg16(weights=weights)
    model.name = args.model

    for param in model.parameters():
        param.requires_grad = False
    model.features[-3].requires_grad = True
    model.features[-2].requires_grad = True
    model.features[-1].requires_grad = True
    model.classifier[-1].requires_grad = True
    model.classifier[-1] = torch.nn.Linear(4096, args.num_classes)
    
    return model

#### MOBILENETV2
def make_mobilenetv2(args):
    weights = torchvision.models.MobileNet_V2_Weights.DEFAULT
    model = torchvision.models.mobilenet_v2(weights=weights)
    model.name = args.model

    for param in model.parameters():
        param.requires_grad = False
    num_ftrs = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(num_ftrs, args.num_classes)
    
    return model

#### INCEPTIONV3
def make_inceptionv3(args):
    weights = torchvision.models.Inception_V3_Weights.DEFAULT
    model = torchvision.models.inception_v3(weights=weights)
    model.name = args.model

    for param in model.parameters():
        param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, args.num_classes)

    return model

#### CONVNEXT SMALL
def make_convnextsmall(args):
    weights = torchvision.models.ConvNeXt_Small_Weights.DEFAULT
    model = torchvision.models.convnext_small(weights=weights)
    model.name = args.model
    
    for param in model.parameters():
        param.requires_grad = False
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, args.num_classes)
    
    return model

#### CONVNEXT SMALL FT
def make_convnextsmall_ft(args):
    weights = torchvision.models.ConvNeXt_Small_Weights.DEFAULT
    model = torchvision.models.convnext_small(weights=weights)
    model.name = args.model

    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, args.num_classes)
    
    return model

#### EFFICIENTNETB0
def make_efficientnetb0(args):
    weights = torchvision.models.EfficientNet_B0_Weights.DEFAULT
    model = torchvision.models.efficientnet_b0(weights=weights )
    model.name = args.model

    model.classifier[1] = nn.Linear(model.classifier[1].in_features, args.num_classes)
    
    return model

#### EFFICIENTNETB3
def make_efficientnetb3(args):
    weights = torchvision.models.EfficientNet_B3_Weights.DEFAULT
    model = torchvision.models.efficientnet_b3(weights=weights)
    model.name = args.model

    model.classifier[1] = nn.Linear(model.classifier[1].in_features, args.num_classes)
    
    return model
