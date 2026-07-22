import torch

def Postprocessing(prediction):
    # Implement your postprocessing logic here
    # For example, you can convert the prediction to a specific format or apply any necessary transformations
    return torch.sigmoid(prediction)