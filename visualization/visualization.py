import cv2
import numpy as np
import matplotlib.pyplot as plt

def overlay(image, mask):
    fig, ax = plt.subplots(figsize=(8,15))
    ax.imshow(image, cmap='gray')
    ax.imshow(mask, cmap='jet', alpha=0.5) 
    plt.axis('off')
    plt.show()
    
def overlay_with_bbox(image, mask, bbox_coords):
    fig, ax = plt.subplots(figsize=(8,15))
    ax.imshow(image, cmap='gray')
    ax.imshow(mask, cmap='jet', alpha=0.5) 
    x_min, y_min, x_max, y_max = bbox_coords
    rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, edgecolor='red', facecolor='none', linewidth=2)
    ax.add_patch(rect)
    plt.axis('off')
    plt.show()