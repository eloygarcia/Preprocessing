
import ast
import csv
import random
import sys

from pathlib import Path
import argparse
import csv

import numpy as np
import pydicom
from PIL import Image
from pydicom.misc import is_dicom

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from utils.image.visualization import DEFAULT_INBREAST_IMAGES_DIR

def find_dicom_images(images_dir: str | Path = DEFAULT_INBREAST_IMAGES_DIR,
                      recursive: bool = True,
                      include_extensionless: bool = False) -> list[Path]:
    """
    List all DICOM images in a directory, optionally searching recursively.

    Parameters:
        images_dir (str | Path): The directory to search for DICOM images.
        recursive (bool): Whether to search recursively.
        include_extensionless (bool): Whether to include files without extensions that are DICOM images.
    Returns:
        list[Path]: A list of paths to DICOM images.
    """
    images_path = Path(images_dir).expanduser()
    if not images_path.exists():
        raise FileNotFoundError(f"Images directory not found: {images_path}")

    dicom_paths: list[Path]
    if not include_extensionless:
        if recursive:
            dicom_paths = sorted(images_path.rglob("*.dcm")) + sorted(images_path.rglob("*.dicom"))
        else:
            dicom_paths = sorted(images_path.glob("*.dcm")) + sorted(images_path.glob("*.dicom"))
    else:
        if recursive:
            dicom_paths = [f for f in images_path.rglob("*") if f.is_file() and is_dicom(f)]
        else:
            dicom_paths = [f for f in images_path.glob("*") if f.is_file() and is_dicom(f)]
        # dicom_paths = [f for f in Path(images_dir).glob("*") if f.is_file() and is_dicom(f)]
    
    if len(dicom_paths) == 0:
        raise FileNotFoundError(f"No DICOM images were found in: {images_path}")
    
    return dicom_paths
