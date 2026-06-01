from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pydicom


DEFAULT_INBREAST_IMAGES_DIR = Path("~/Escritorio/Datasets/InBreast/Images").expanduser()


def list_dicom_images(images_dir: str | Path = DEFAULT_INBREAST_IMAGES_DIR) -> list[Path]:
    images_path = Path(images_dir).expanduser()
    if not images_path.exists():
        raise FileNotFoundError(f"Images directory not found: {images_path}")

    dicom_paths = sorted(images_path.glob("*.dcm"))
    if not dicom_paths:
        raise FileNotFoundError(f"No DICOM images were found in: {images_path}")

    return dicom_paths


def load_dicom_image(image_path: str | Path) -> np.ndarray:
    dicom_path = Path(image_path).expanduser()
    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    dataset = pydicom.dcmread(dicom_path)
    image = dataset.pixel_array.astype(np.float32)

    if getattr(dataset, "PhotometricInterpretation", "") == "MONOCHROME1":
        image = image.max() - image

    image -= image.min()
    max_value = image.max()
    if max_value > 0:
        image /= max_value

    return image


def show_dicom_image(
    image_path: str | Path | None = None,
    image_index: int = 0,
    images_dir: str | Path = DEFAULT_INBREAST_IMAGES_DIR,
    figsize: tuple[int, int] = (8, 8),
    cmap: str = "gray",
):
    dicom_paths = list_dicom_images(images_dir)

    if image_path is None:
        try:
            selected_path = dicom_paths[image_index]
        except IndexError as error:
            raise IndexError(
                f"image_index {image_index} is out of range for {len(dicom_paths)} images"
            ) from error
    else:
        selected_path = Path(image_path).expanduser()

    image = load_dicom_image(selected_path)

    figure, axis = plt.subplots(figsize=figsize)
    axis.imshow(image, cmap=cmap)
    axis.set_title(selected_path.name)
    axis.axis("off")
    figure.tight_layout()

    return figure, axis, image