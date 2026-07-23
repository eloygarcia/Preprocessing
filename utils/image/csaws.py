from pathlib import Path
import csv

import numpy as np
from PIL import Image


DEFAULT_CSAWS_DATASET_DIR = Path("~/Escritorio/Datasets/CsawS/anonymized_dataset").expanduser()
DEFAULT_CSAWS_WHOLE_BREAST_MASKS_DIR = Path("~/Escritorio/Datasets/CsawS/whole_breast_mask").expanduser()
DEFAULT_CSAWS_SUMMARY_EXPORT_PATH = Path("~/Escritorio/Trabajos/Preprocessing/data/csaws_image_summary.csv").expanduser()

DEFAULT_CSAWS_LABELS = (
    "mammary_gland",
    "pectoral_muscle",
)

DEFAULT_CSAWS_SUMMARY_FIELDS = (
    "file_name",
    "image_path",
    "numpy_nrow",
    "numpy_ncol",
    "numpy_max_value",
    "rows_match",
    "cols_match",
    "max_match",
    "pixel_array_shape",
    "pixel_array_dtype",
)


def list_csaws_images(dataset_dir: str | Path = DEFAULT_CSAWS_DATASET_DIR) -> list[Path]:
    dataset_path = Path(dataset_dir).expanduser()
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_path}")

    image_paths = sorted(
        path
        for path in dataset_path.glob("*/*.png")
        if path.stem.count("_") == 1
    )

    if not image_paths:
        raise FileNotFoundError(f"No CSAWS base images were found in: {dataset_path}")

    return image_paths


def load_csaws_image(image_path: str | Path) -> np.ndarray:
    path = Path(image_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    return np.array(Image.open(path))


def collect_csaws_image_summary_record(image_path: str | Path) -> dict[str, str]:
    path = Path(image_path).expanduser()
    image = load_csaws_image(path)

    return {
        "file_name": path.name,
        "image_path": str(path),
        "numpy_nrow": str(image.shape[0]) if image.ndim >= 1 else "",
        "numpy_ncol": str(image.shape[1]) if image.ndim >= 2 else "",
        "numpy_max_value": str(np.max(image)),
        "rows_match": "",
        "cols_match": "",
        "max_match": "",
        "pixel_array_shape": "x".join(str(dimension) for dimension in image.shape),
        "pixel_array_dtype": str(image.dtype),
    }


def export_csaws_image_summary_dataset(
    image_paths: list[str | Path],
    output_path: str | Path = DEFAULT_CSAWS_SUMMARY_EXPORT_PATH,
    fieldnames: tuple[str, ...] | list[str] = DEFAULT_CSAWS_SUMMARY_FIELDS,
) -> Path:
    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(fieldnames))
        writer.writeheader()

        for image_path in image_paths:
            record = collect_csaws_image_summary_record(image_path)
            writer.writerow({field: record.get(field, "") for field in fieldnames})

    return destination


def get_csaws_label_path(image_path: str | Path, label_name: str) -> Path:
    path = Path(image_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    label_path = path.with_name(f"{path.stem}_{label_name}.png")
    if not label_path.exists():
        raise FileNotFoundError(f"Label not found: {label_path}")

    return label_path


def load_csaws_label(image_path: str | Path, label_name: str) -> np.ndarray:
    label_path = get_csaws_label_path(image_path, label_name)
    label_array = np.array(Image.open(label_path))

    return label_array > 0


def create_csaws_combined_mask(
    image_path: str | Path,
    mammary_label: int = 1,
    pectoral_label: int = 2,
) -> np.ndarray:
    image = load_csaws_image(image_path)
    mammary_mask = load_csaws_label(image_path, "mammary_gland")
    pectoral_mask = load_csaws_label(image_path, "pectoral_muscle")

    if mammary_mask.shape != image.shape or pectoral_mask.shape != image.shape:
        raise ValueError("Image and CSAWS label masks must have the same shape")

    combined_mask = np.zeros(image.shape, dtype=np.uint8)
    combined_mask[mammary_mask] = mammary_label
    combined_mask[pectoral_mask] = pectoral_label

    return combined_mask


def find_first_csaws_case_with_pectoral_mask(
    dataset_dir: str | Path = DEFAULT_CSAWS_DATASET_DIR,
) -> Path:
    for image_path in list_csaws_images(dataset_dir):
        pectoral_mask = load_csaws_label(image_path, "pectoral_muscle")
        if np.any(pectoral_mask):
            return image_path

    raise FileNotFoundError("No CSAWS image with a non-empty pectoral_muscle mask was found")


def get_csaws_mask_output_path(
    image_path: str | Path,
    output_dir: str | Path = DEFAULT_CSAWS_WHOLE_BREAST_MASKS_DIR,
) -> Path:
    path = Path(image_path).expanduser()
    destination_dir = Path(output_dir).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    destination_dir.mkdir(parents=True, exist_ok=True)

    return destination_dir / path.name


def save_csaws_combined_mask(
    image_path: str | Path,
    output_dir: str | Path = DEFAULT_CSAWS_WHOLE_BREAST_MASKS_DIR,
) -> Path:
    combined_mask = create_csaws_combined_mask(image_path)
    output_path = get_csaws_mask_output_path(image_path, output_dir=output_dir)
    Image.fromarray(combined_mask, mode="L").save(output_path)

    return output_path


def save_csaws_dataset_combined_masks(
    image_paths: list[str | Path],
    output_dir: str | Path = DEFAULT_CSAWS_WHOLE_BREAST_MASKS_DIR,
) -> list[Path]:
    saved_paths = []

    for image_path in image_paths:
        saved_paths.append(save_csaws_combined_mask(image_path, output_dir=output_dir))

    return saved_paths