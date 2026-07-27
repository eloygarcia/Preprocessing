import cv2
import numpy as np
from PIL import Image
import torch
import torchvision
from torchvision import transforms
#import albumentations as transforms

import src.data_loading.augmentations as augmentations
from src.data_loading.loading import standard_normalize_single_image

def f_transform_val():
    return transforms.Compose([
            transforms.ToTensor(),
        ])

def standard_normalize_single_image(image):
    """
    Standardizes an image in-place 
    """
    image -= np.mean(image)
    image /= np.maximum(np.std(image), 10**(-5))
    return image

def Preprocessing(image):
    # Implement your preprocessing logic here
    # For example, you can convert the study to a specific format or apply any necessary transformations
    
    image = image.astype(np.float32)
    best_center=[100,1920]
    view = "L-MLO"

    cropped_image, _ = augmentations.random_augmentation_best_center(
        image=image,
        input_size=image.shape,
        random_number_generator=np.random.RandomState(0),
        best_center=best_center,
        view=view
    )
    cropped_image = standard_normalize_single_image(cropped_image)
    
    return torch.Tensor(np.expand_dims(np.expand_dims(cropped_image, 0), 0).copy())
