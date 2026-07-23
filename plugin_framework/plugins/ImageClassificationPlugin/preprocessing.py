
import torchvision
from torchvision import transforms
#import albumentations as transforms
import cv2

def f_transform_val(new_size=(1024, 512)):
    return transforms.Compose([
            transforms.Resize(new_size),            
            transforms.ToTensor(),
            #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),            
        ])

def Preprocessing(image, model='resnet50'):
    # Implement your preprocessing logic here
    # For example, you can convert the study to a specific format or apply any necessary transformations

    # model = 'resnet50'  # Default model

    ## Transformations 
    new_size = (1024, 512) # resnet50, vgg16, mobilenetv2 = 224, inception_v3 = 299
    if model == 'mobilenetv2':
        new_size = (224,224)
    if model == 'inceptionv3':
        new_size = (299,299)

    transform = f_transform_val(new_size=new_size)

    #image = read_image(img_path)
    #image = image.float()
    image = transform(image)
    image = image.unsqueeze(0)

    return image