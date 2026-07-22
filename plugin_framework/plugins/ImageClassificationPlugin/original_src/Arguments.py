import os
import argparse

def arguments():

    parser = argparse.ArgumentParser(description='Nueral Network classification for breast abnormalities')
    
    parser.add_argument('--train_lib', type=str, default='', help='path to train library binary')
    parser.add_argument('--val_lib', type=str, default='', help='path to validation library binary. If present.')
    parser.add_argument('--test_lib', type=str, default='', help='path to test library binary. If present.')

    parser.add_argument('--save_path', type=str, default='.', help='name of output file')
    
    parser.add_argument('--device', type=str, default='cuda', help='device to use for training (default: cuda)')
    
    ## Model parameters
    parser.add_argument('--model', type=str, default='resnet50', help='model to use for MIL (default: resnet50, options: resnet50, resnet50_ft, resnet18_ft vgg16, vgg16_ft, mobilenetv2, inceptionv3, efficientnetb0, efficientnetb3, convnextsmall, convnextsmall_ft)')
    parser.add_argument('--pretrained', action='store_true', help='use pretrained model weights (default: False)')
    parser.add_argument('--weights_path', type=str, default='', help='path to model weights (default: empty, no weights loaded)')
    parser.add_argument('--num_classes', type=int, default=11, help='number of classes for classification (default: 11)')

    ## Training parameters
    parser.add_argument('--batch_size', type=int, default=16, help='mini-batch size (default: 16)')
    parser.add_argument('--num_epochs', type=int, default=10, help='number of epochs (default: 10)')
    parser.add_argument('--workers', default=0, type=int, help='number of data loading workers (default: 0)')
    parser.add_argument('--test_every', default=10, type=int, help='test on val every (default: 10)')
    parser.add_argument('--weights', default=0.2, type=float, help='unbalanced positive class weight (default: 0.2, balanced classes)')
    parser.add_argument('--lr', default=1e-4, type=float, help='Learning rate (default: 1e-4)')
    parser.add_argument('--momentum', default=0.9, type=float, help='SDG momentum (default: 0.9)')
    parser.add_argument('--weight_decay', default=1e-5, type=float, help='Weight decay (default: 1e-5)')
    parser.add_argument('--threshold', default=0.3, type=float, help='Threshold for binary classification (default: 0.3)')

    ## Metrics 
    parser.add_argument('--best_loss', default=1e8, type=float, help='best loss (default: 1e8)')
    parser.add_argument('--best_acc', default=0.0, type=float, help='best accuracy (default: 0.0)')
    parser.add_argument('--best_kappa', default=0.0, type=float, help='best kappa (default: 0.0)')
    parser.add_argument('--best_hamming', default=10.0, type=float, help='best hamming (default: 10.0)')

    ## Early stopping parameters
    parser.add_argument('--early_stop_patience',default=10, type=int, help='early stopping patience (default: 10)')
    parser.add_argument('--early_stop_c', default=0, type=int, help='early stopping count (default: 0)')

    arg = parser.parse_args()
    return arg