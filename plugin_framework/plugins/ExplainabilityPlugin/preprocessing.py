
import torchvision
from torchvision import transforms
#import albumentations as transforms
import cv2

import numpy as np
from PIL import Image


def f_transform_val(new_size=(1024, 512)):
    return transforms.Compose([
            transforms.Resize(new_size),            
            transforms.ToTensor(),
            #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),            
        ])


def _choose_new_size(model):
    new_size = (1024, 512) # resnet50, vgg16, mobilenetv2 = 224, inception_v3 = 299
    if model == 'mobilenetv2':
        new_size = (224,224)
    if model == 'inceptionv3':
        new_size = (299,299)
    return new_size


def Preprocessing(image, metadata, config=None):
    # Implement your preprocessing logic here
    # For example, you can convert the study to a specific format or apply any necessary transformations
    image = image.astype(np.float32) 
    image = 255*(image - image.min()) / (image.max() - image.min())  # Normalize to [0, 1]

    model = config['model']
    new_size = _choose_new_size(model)

    if isinstance(image, np.ndarray):
        image = Image.fromarray(image).convert("RGB")

    transform = f_transform_val(new_size=new_size)

    image = transform(image)
    image = image.unsqueeze(0)

    return image