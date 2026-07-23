"""
Explainability module for breast abnormality classification
Uses SHAP and Grad-CAM for comprehensive interpretability
"""

import os
import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
import cv2
from tqdm import tqdm
from pathlib import Path

# XAI Libraries
import shap
from captum.attr import GradCAM, IntegratedGradients, Saliency
from captum.attr import visualization as viz

from models import *
from Transforms import *
from Datasets import *
from MultiModels import MultiModel
from Arguments import arguments


class ExplainabilityEngine:
    """
    Comprehensive explainability engine for the mammography classification model.
    Supports multiple XAI methods: Grad-CAM, SHAP, Saliency, Integrated Gradients
    """
    
    def __init__(self, model, device, model_name='resnet50'):
        self.model = model
        self.device = device
        self.model_name = model_name
        
    def gradcam_attribution(self, input_tensor, target_layer, target_class=None):
        """
        Generate Grad-CAM heatmap
        
        Args:
            input_tensor: Input image tensor (B, C, H, W)
            target_layer: Layer to apply Grad-CAM on
            target_class: Target class for attribution (None for predicted)
        
        Returns:
            cam: CAM heatmap (H, W)
        """
        grad_cam = GradCAM(self.model, target_layer)
        attributions = grad_cam.attribute(input_tensor, target=target_class)
        
        # Sum across channels and normalize
        cam = attributions.squeeze(0).abs().mean(dim=0).cpu().detach().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-10)
        
        return cam
    
    def integrated_gradients_attribution(self, input_tensor, target_class=None, n_steps=50):
        """
        Integrated Gradients attribution
        
        Args:
            input_tensor: Input image tensor
            target_class: Target class
            n_steps: Number of integration steps
            
        Returns:
            attributions: Attribution map
        """
        ig = IntegratedGradients(self.model)
        attributions = ig.attribute(input_tensor, target=target_class, n_steps=n_steps)
        
        # Process attributions
        attr_map = attributions.squeeze(0).abs().mean(dim=0).cpu().detach().numpy()
        attr_map = (attr_map - attr_map.min()) / (attr_map.max() - attr_map.min() + 1e-10)
        
        return attr_map
    
    def saliency_attribution(self, input_tensor, target_class=None):
        """
        Saliency map attribution
        
        Args:
            input_tensor: Input image tensor
            target_class: Target class
            
        Returns:
            saliency: Saliency map
        """
        saliency = Saliency(self.model)
        attributions = saliency.attribute(input_tensor, target=target_class)
        
        saliency_map = attributions.squeeze(0).abs().mean(dim=0).cpu().detach().numpy()
        saliency_map = (saliency_map - saliency_map.min()) / (saliency_map.max() - saliency_map.min() + 1e-10)
        
        return saliency_map
    
    def shap_attribution(self, input_tensor, background_size=50):
        """
        SHAP Deep Explainer attribution
        
        Args:
            input_tensor: Input image tensor (single sample)
            background_size: Size of background dataset
            
        Returns:
            shap_values: SHAP values
        """
        # Create background dataset
        background = torch.randn((background_size, *input_tensor.shape[1:])).to(self.device)
        
        explainer = shap.DeepExplainer(self.model, background)
        shap_values = explainer.shap_values(input_tensor)
        
        return shap_values
    
    @staticmethod
    def overlay_heatmap(image_np, heatmap, alpha=0.5, cmap='jet'):
        """
        Overlay heatmap on original image
        
        Args:
            image_np: Original image (H, W, 3) normalized to [0, 1]
            heatmap: Heatmap (H, W) normalized to [0, 1]
            alpha: Transparency of heatmap
            cmap: Colormap name
            
        Returns:
            overlay: Overlayed image (H, W, 3)
        """
        # Ensure image is in [0, 1]
        if image_np.max() > 1:
            image_np = image_np / 255.0
        
        # Apply colormap to heatmap
        colormap = cm.get_cmap(cmap)
        heatmap_colored = colormap(heatmap)[:, :, :3]
        
        # Resize heatmap to match image if needed
        if heatmap_colored.shape != image_np.shape:
            heatmap_colored = cv2.resize(heatmap_colored, 
                                        (image_np.shape[1], image_np.shape[0]))
        
        # Overlay
        overlay = (1 - alpha) * image_np + alpha * heatmap_colored
        overlay = np.clip(overlay, 0, 1)
        
        return overlay
    
    @staticmethod
    def show_attribution_map(image_np, attribution_map, title="Attribution Map", 
                            save_path=None, figsize=(12, 4)):
        """
        Visualize original image and attribution map side by side
        
        Args:
            image_np: Original image (H, W, 3) or (H, W)
            attribution_map: Attribution map (H, W)
            title: Figure title
            save_path: Path to save figure
            figsize: Figure size
        """
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        fig.suptitle(title, fontsize=16)
        
        # Normalize image if needed
        if image_np.ndim == 3 and image_np.max() > 1:
            image_np = image_np / 255.0
        elif image_np.ndim == 2:
            image_np = np.stack([image_np] * 3, axis=-1)
        
        # Original image
        axes[0].imshow(image_np, cmap='gray')
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Attribution map
        im = axes[1].imshow(attribution_map, cmap='jet')
        axes[1].set_title('Attribution Map')
        axes[1].axis('off')
        plt.colorbar(im, ax=axes[1])
        
        # Overlay
        overlay = ExplainabilityEngine.overlay_heatmap(image_np, attribution_map, 
                                                       alpha=0.6, cmap='jet')
        axes[2].imshow(overlay)
        axes[2].set_title('Overlay')
        axes[2].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        plt.show()
    
    @staticmethod
    def show_multiple_attributions(image_np, attributions_dict, title="Model Attributions",
                                  save_path=None, figsize=(16, 6)):
        """
        Compare multiple attribution methods side by side
        
        Args:
            image_np: Original image
            attributions_dict: Dict with method_name -> attribution_map
            title: Figure title
            save_path: Path to save figure
            figsize: Figure size
        """
        num_methods = len(attributions_dict) + 1
        fig, axes = plt.subplots(1, num_methods, figsize=figsize)
        fig.suptitle(title, fontsize=16)
        
        # Normalize image if needed
        if image_np.ndim == 3 and image_np.max() > 1:
            image_np = image_np / 255.0
        elif image_np.ndim == 2:
            image_np = np.stack([image_np] * 3, axis=-1)
        
        # Original
        axes[0].imshow(image_np, cmap='gray')
        axes[0].set_title('Original')
        axes[0].axis('off')
        
        # Attributions
        for idx, (method_name, attr_map) in enumerate(attributions_dict.items(), 1):
            im = axes[idx].imshow(attr_map, cmap='jet')
            axes[idx].set_title(method_name)
            axes[idx].axis('off')
            plt.colorbar(im, ax=axes[idx], fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        plt.show()


def get_target_layer(model, model_name):
    """
    Get the appropriate target layer for Grad-CAM based on model architecture
    
    Args:
        model: PyTorch model
        model_name: Name of the model
        
    Returns:
        target_layer: Layer for Grad-CAM attribution
    """
    if 'resnet' in model_name.lower():
        # For ResNet models
        if hasattr(model, 'features'):
            return model.features[-1][-1]
        elif hasattr(model, 'backbone'):
            return model.backbone.layer4[-1]
    elif 'efficientnet' in model_name.lower():
        if hasattr(model, 'features'):
            return model.features[-1]
    elif 'mobilenet' in model_name.lower():
        if hasattr(model, 'features'):
            return model.features[-1]
    
    # Fallback to last layer
    return list(model.modules())[-2]


def main():
    print('Mammography Classification - Explainability Analysis')
    print('')
    
    # Parse arguments
    args = arguments()
    for key in args.__dict__.keys():
        print(f"{key}: {args.__dict__[key]}")
    print('')
    
    # Set device
    args.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {args.device}")
    
    # Transformations
    new_size = (1024, 512)
    if args.model == 'mobilenetv2':
        new_size = (224, 224)
    elif args.model == 'inceptionv3':
        new_size = (299, 299)
    
    transform_val = f_transform_val(new_size=new_size)
    
    # Load model
    print("Loading model...")
    model = MultiModel(args=args)
    model = model.to(args.device)
    
    if args.pretrained:
        model.load_state_dict(torch.load(args.weights_path, map_location=args.device))
    
    model.eval()
    
    # Load validation dataset
    print("Loading validation dataset...")
    val_dataset = CustomDataset(args.test_lib, transform=transform_val)
    
    # Initialize explainability engine
    xai_engine = ExplainabilityEngine(model=model, device=args.device, 
                                      model_name=args.model)
    target_layer = get_target_layer(model, args.model)
    
    # Select samples to explain
    num_samples = min(10, len(val_dataset))  # Explain first 10 samples
    
    print(f"\nGenerating attributions for {num_samples} samples...")
    
    for idx in tqdm(range(num_samples)):
        # Get sample
        image, label = val_dataset[idx]
        image_batch = image.unsqueeze(0).to(args.device)
        image_np = image.permute(1, 2, 0).cpu().numpy()
        
        # Get model prediction
        with torch.no_grad():
            logits = model(image_batch)
            probs = torch.sigmoid(logits)
        
        pred_class = (probs > 0.5).int().squeeze(0).cpu().numpy()
        
        # Generate attributions using different methods
        print(f"\nSample {idx + 1}/{num_samples}")
        print(f"Predicted: {pred_class}, Ground Truth: {label}")
        
        try:
            # Grad-CAM
            gradcam_attr = xai_engine.gradcam_attribution(image_batch, target_layer)
            
            # Integrated Gradients
            ig_attr = xai_engine.integrated_gradients_attribution(image_batch, n_steps=30)
            
            # Saliency
            saliency_attr = xai_engine.saliency_attribution(image_batch)
            
            # Compare attributions
            attributions = {
                'Grad-CAM': gradcam_attr,
                'Integrated Gradients': ig_attr,
                'Saliency': saliency_attr
            }
            
            # Visualize
            output_dir = Path(args.output_dir) / 'xai_results' / f'sample_{idx:04d}'
            xai_engine.show_multiple_attributions(
                image_np, 
                attributions,
                title=f'Attribution Methods Comparison - Sample {idx}',
                save_path=str(output_dir / 'all_methods.png')
            )
            
            # Show individual overlays
            for method_name, attr_map in attributions.items():
                xai_engine.show_attribution_map(
                    image_np,
                    attr_map,
                    title=f'{method_name} - Sample {idx}',
                    save_path=str(output_dir / f'{method_name.replace(" ", "_")}.png')
                )
        
        except Exception as e:
            print(f"Error processing sample {idx}: {str(e)}")
            continue
    
    print("\nExplainability analysis complete!")
    print(f"Results saved to: {args.output_dir}/xai_results/")


if __name__ == '__main__':
    main()
