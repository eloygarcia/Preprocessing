import cv2
import numpy as np
import torch

def Postprocessing(prediction):
    # Implement your postprocessing logic here
    # For example, you can convert the prediction to a specific format or apply any necessary transformations

    return prediction.cpu().detach().numpy()[0,1]
    # return torch.sigmoid(prediction)
    # return prediction.argmax(dim=1).squeeze(0)