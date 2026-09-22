import cv2
import numpy as np
import matplotlib.pyplot as plt

def image_with_bboxes(image, detections):
    fig, ax = plt.subplots(figsize=(8,15))
    ax.imshow(image, cmap='gray')
    for i in range(int(detections["num_detections"])):
        x_min, y_min, x_max, y_max = detections["boxes"][i]
        rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, edgecolor='red', facecolor='none', linewidth=2)
        ax.add_patch(rect)
        ax.text(x_min, y_min - 5, f"bbox {i+1}: {detections['scores'][i]:.2f}", color='red', fontsize=12)
    plt.axis('off')
    plt.show()

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