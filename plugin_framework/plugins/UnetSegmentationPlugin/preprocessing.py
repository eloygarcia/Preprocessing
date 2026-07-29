
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
            # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),            
        ])

def Preprocessing(image,metadata):
    image = image.astype(np.float32)
    image = (image - image.min()) / (image.max() - image.min())  ### Es el puto windowing!!
    ## Toda esta mierda te está fallando por el puto windowing + la normalización entre [0,1]

    if isinstance(image, np.ndarray):
        print(image.shape)
        image = Image.fromarray(image)


    image_size = image.size
    new_size = (image_size[1] // 4, image_size[0] // 4)

    if ('pixel_spacing' in metadata.keys() )  and (metadata['pixel_spacing']!= None):
        new_size = (int(image_size[1]*metadata['pixel_spacing'][1]//0.4), int(image_size[0]*metadata['pixel_spacing'][0]//0.4))

    print(new_size)
    #print(metadata['laterality'])

    if metadata['laterality'] == "R":
       image = image.transpose(Image.FLIP_LEFT_RIGHT)

    transform = f_transform_val(new_size=new_size)

    image = transform(image)
    image = image.unsqueeze(0)

    return image