import os
import numpy as np
import pandas as pd
from PIL import Image
from ast import literal_eval

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
from torchvision.transforms.functional import pil_to_tensor, to_tensor

from skimage.io import imread
from skimage.color import gray2rgb
from skimage.transform import resize

from torchvision.io import read_image

class CustomDataset(Dataset):
    def __init__(self, file='', transform=None):
        """
        Args:
            file (csv file):
            transform:
        """
        self.file = file
        self.info = pd.read_csv(file,
                                converters={'finding_categories': literal_eval})
        self.transform = transform

        #self.basedir = '/home/eloygarcia/Escritorio/Synthetic Patient/VinDr_cropped'
        self.basedir = '/home/data/VinDr_cropped'

    def __len__(self):
        return len(self.info)

    def __getitem__(self, idx):
        study_id = self.info.iloc[idx]['study_id']
        image_id = self.info.iloc[idx]['image_id']

        image_path = os.path.join( self.basedir, study_id, image_id + '.png')
        # image_path = self.info.iloc[idx]['ImagePath']
        #print(image_path)
        #print(os.path.exists(image_path))
        
        ### label formation
        label = []
        label.append( self.info.iloc[idx]['No_Finding'])

        #label.append( np.abs(self.info.iloc[idx]['No_Finding']-1))
        label.append( self.info.iloc[idx]['Mass'])
        
        # label.append( self.info.iloc[idx]['Global_Asymmetry'] )
        tt = self.info.iloc[idx]['Global_Asymmetry'] + self.info.iloc[idx]['Asymmetry']
        label.append( 1.0 if tt>0 else 0.0 )
        
        #label.append( self.info.iloc[idx]['Suspicious_Calcification'])
        label.append( self.info.iloc[idx]['Architectural_Distortion'])
        
        label.append( self.info.iloc[idx]['Focal_Asymmetry'])
        
        # label.append( self.info.iloc[idx]['Skin_Thickening'])
        tt2 = self.info.iloc[idx]['Skin_Thickening'] + self.info.iloc[idx]['Skin_Retraction']
        label.append( 1.0 if tt2>0 else 0.0 )

        label.append( self.info.iloc[idx]['Nipple_Retraction'])
        # label.append( self.info.iloc[idx]['Suspicious_Lymph_Node'])
        # label.append( self.info.iloc[idx]['Skin_Retraction'])
        
        #label.append( self.info.iloc[idx]['Asymmetry'])
        

        img = Image.open(image_path).convert('RGB')

        img = self.transform(img)
        label = np.array(label).astype(np.float32)

        return {
            'image':img,
            'label':label,
            'image_path': image_path
        }


class CustomDatasetValidation(Dataset):
    def __init__(self, dataframe, transform):
        self.transform = transform
        self.dataframe = dataframe

        self.images = self.dataframe['path'].tolist()
        self.labels = self.dataframe['label'].astype(int).tolist()
        self.width = self.dataframe['width'].astype(int).tolist()
        self.height = self.dataframe['height'].astype(int).tolist()
        self.x1 = self.dataframe['x1'].astype(int).tolist()
        self.y1 = self.dataframe['y1'].astype(int).tolist()
        self.x2 = self.dataframe['x2'].astype(int).tolist()
        self.y2 = self.dataframe['y2'].astype(int).tolist()
        self.crop_x = self.dataframe['crop_x'].astype(int).tolist()
        self.crop_y = self.dataframe['crop_y'].astype(int).tolist()

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        width = self.width[idx]
        height = self.height[idx]
        x1 = self.x1[idx]
        y1 = self.y1[idx]
        x2 = self.x2[idx]
        y2 = self.y2[idx]
        crop_x = self.crop_x[idx]
        crop_y = self.crop_y[idx]
        
        image = read_image(img_path)
        image = image.float()
        image = self.transform(image)

        return {
            'image': image,
            'label': label,
            'width' : width,
            'height' : height,
            'x1' : x1,
            'y1' : y1,
            'x2' : x2,
            'y2' : y2,
            'crop_x': crop_x,
            'crop_y': crop_y
        }
    

if __name__=='__main__':
    info_csv = '/home/eloygarcia/Escritorio/Synthetic Patient/Data/bilateral_subset.csv'
    # loader = DataLoader(CustomDataset(info_csv))
    dataset = CustomDataset(info_csv)
    #print(len(dataset))
    loader = DataLoader(dataset, batch_size=1, shuffle =False, num_workers=0)

    for i, sample in enumerate(loader):
        print(i)
        batch_list = []
        print(sample[1])
        batch = torch.cat(sample[0], 0)
        print(batch.squeeze().size())


