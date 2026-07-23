import copy
import logging
import time
from tqdm import tqdm
import json

import matplotlib
matplotlib.use('Agg')  # backend sin display

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
import cv2 as cv

import torch
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import Dataset, DataLoader
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
import torch.nn.functional as F

import pytorch_lightning as pl
from sklearn.metrics import (
    accuracy_score, 
    cohen_kappa_score, 
    roc_auc_score, 
    hamming_loss,
    precision_recall_curve,
    f1_score,
)

from models import *
from aux_functions import *

from Transforms import *
from Datasets import *
from MultiModels import MultiModel
from Arguments import arguments

def main():
    print('Trying Breast abnormality classification with cnn')
    print('')

    ## Argument parser:
    args = arguments()
    for key in args.__dict__.keys():
        print(key+' : '+str(args.__dict__[key]) )
    print('')

    # Set device
    args.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {args.device}")

    ## Transfromations 
    new_size = (1024, 512) # resnet50, vgg16, mobilenetv2 = 224, inception_v3 = 299
    if args.model == 'mobilenetv2':
        new_size = (224,224)
    if args.model == 'inceptionv3':
        new_size = (299,299)

    transform_val = f_transform_val(new_size=new_size)

    ## Load model
    model = MultiModel(args=args)
    model = model.to(args.device)
    
    if args.pretrained:
        print(args.weights_path)
        model.load_state_dict(torch.load(args.weights_path, map_location=args.device))
    model.eval()

    ## Validation dataset and loader
    val_dataset = CustomDataset(args.test_lib, 
                                  transform=transform_val)
    val_dataloader = DataLoader( val_dataset,
                                   batch_size = args.batch_size,
                                   shuffle = False,
                                   num_workers = args.workers)
    
    # TO STORE THE LABELS, PREDICTIONS AND PROBABILITIES
    running_labels = []
    running_preds = []
    running_probs = []
    running_probs_neg = []
    running_probs_pos = []

    # ITERATE OVER DATA
    with torch.no_grad():
        for batch in tqdm(val_dataloader):
            inputs = batch["image"].to(args.device)
            labels = batch["label"].to(args.device)

            #inputs = torch.cat((inputs, inputs, inputs), dim=1)
            outputs = model(inputs)
            outputs_sig = torch.sigmoid(outputs)
            #preds = ((outputs_sig>0.5)*1).float()
            
            print(outputs_sig.mean())
            preds = outputs_sig.detach()>args.threshold ## multi-label classification
            #preds = outputs.detach()>0.5 ## multi-label classification
            
            running_labels.append(labels.int().cpu().numpy())
            running_probs.append(outputs_sig.cpu().numpy())
            running_preds.append(preds.int().cpu().numpy())
            
            # print("")
            # print(preds.int())
            # print(labels.int())
            # print("")

            #running_probs_neg   = running_probs_neg + outputs_sig[labels.int().cpu().numpy() == 0].cpu().numpy() # .tolist()
            #running_probs_pos   = running_probs_pos + outputs_sig[labels.int().cpu().numpy() == 1].cpu().numpy() # .tolist()

    # concatenar todo
    all_outputs = np.vstack(running_probs)
    all_labels = np.vstack(running_labels)
    all_preds = np.vstack(running_preds)

        
    # epoch_kappa = cohen_kappa_score(running_labels, running_preds) # kappa of the epoch
    # epoch_hamming = hamming_loss(running_labels, running_preds) # Hamming loss for multi-label classificatin
    # epoch_f1 = f1_score(running_labels, running_preds, average='micro')

    #print(running_labels)
    #print(running_preds)

    ## Copilot
    # https://scikit-learn.org/0.15/auto_examples/plot_roc.html
    # Compute ROC curve and ROC area for each class
    
    num_classes = args.num_classes
    thresholds = []

    #plt.figure(figsize=(10, 8))
    plt.figure()
    roc_data = {}

    for i in range(num_classes):
        fpr, tpr, thr = roc_curve(all_labels[:, i], all_outputs[:, i])
        roc_auc = auc(fpr, tpr)
        print(f'Clase {i} (AUC = {roc_auc:.2f})')
        
        # maximizar TPR - FPR (Youden index)
        optimal_idx = np.argmax(tpr - fpr)
        thresholds.append(thr[optimal_idx])
        print(f"Optimal threshold for class {i}: th = {thr[optimal_idx]}")
        print(" ")

        plt.plot(fpr, tpr, label=f'Clase {i} (AUC = {roc_auc:.2f})')

    plt.plot([0,1], [0,1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC por clase')
    plt.legend()
    # plt.show()

    plt.savefig(os.path.join(os.path.dirname(args.weights_path),"roc_curves.png"), dpi=300)
    plt.close()


    ## Precision Recall curve
    plt.figure()
    pr_data = {}
    for i in range(num_classes):
        precision, recall, thrs = precision_recall_curve(
            all_labels[:, i],
            all_outputs[:, i]
        )

        pr_data[f"class_{i}"] = {
                "precision": precision,
                "recall": recall,
                "thresholds": thrs
            }

        plt.plot(recall, precision, label=f'Clase {i}')

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    # plt.show()

    plt.savefig(os.path.join(os.path.dirname(args.weights_path),"pr_curves.png"), dpi=300)
    plt.close()



    ##
    print(thresholds)
    preds = np.zeros_like(all_outputs)

    for i in range(num_classes):
        preds[:, i] = (all_outputs[:, i] > thresholds[i]).astype(int)


    ## Something else
    macro_auc = roc_auc_score(all_labels, all_outputs, average='macro')
    micro_auc = roc_auc_score(all_labels, all_outputs, average='micro')

    print("Macro AUC:", macro_auc)
    print("Micro AUC:", micro_auc)
    print("")


    ## Guardar metricas
    def convert_numpy(obj):
        return {k: v.tolist() if isinstance(v, np.ndarray) else v
                for k, v in obj.items()}

    roc_data_json = {k: convert_numpy(v) for k, v in roc_data.items()}
    pr_data_json = {k: convert_numpy(v) for k, v in pr_data.items()}

    with open("roc_data.json", "w") as f:
        json.dump(roc_data_json, f, indent=4)

    with open("pr_data.json", "w") as f:
        json.dump(pr_data_json, f, indent=4)

    for i in range(num_classes):
        df = pd.DataFrame({
            "fpr": roc_data[f"class_{i}"]["fpr"],
            "tpr": roc_data[f"class_{i}"]["tpr"],
            "thresholds": roc_data[f"class_{i}"]["thresholds"]
        })
        df.to_csv(f"roc_class_{i}.csv", index=False)


    metrics = {
        "f1_macro": f1_score(all_labels, preds, average="macro"),
        "f1_micro": f1_score(all_labels, preds, average="micro"),
        "hamming_loss": hamming_loss(all_labels, preds)
    }

    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)


    ## Visualize predictions
    #probs = np.vstack(running_probs)
    #plot_roc(running_labels, probs, True, model.name, n_classes=1)
    lsa = ['No_Finding', 'Mass', 'Global_Asymmetry', 'Suspicious_Calcification', 
           'Architectural_Distortion','Focal_Asymmetry', 'Skin_Thickening', 'Nipple_Retraction', 'Lymph_Node', 
           'Skin_Retraction','Asymmetry']
    #print(len(lsa))

    plot_confusion_matrix(all_labels, preds, lsa[1:num_classes],
                          normalize=False,
                          title='Confusion matrix of the model',
                          cmap=plt.cm.Blues)

    print(all_labels.shape)
    print(preds.shape)
    

if __name__=='__main__':
    main()