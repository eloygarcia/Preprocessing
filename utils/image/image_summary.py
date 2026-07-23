from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import csv

import numpy as np
from PIL import Image


DEFAULT_IMAGE_SUMMARY_FIELDS = (
    "file_name",
    "image_path",
    "parent_dir",
    "image_format",
    "image_mode",
    "numpy_nrow",
    "numpy_ncol",
    "numpy_nchan",
    "numpy_max_value",
    "pixel_array_shape",
    "pixel_array_dtype",
)

DEFAULT_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")


def list_raster_images(
    dataset_dir: str | Path,
    suffixes: tuple[str, ...] = DEFAULT_IMAGE_SUFFIXES,
) -> list[Path]:
    dataset_path = Path(dataset_dir).expanduser()
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_path}")

    normalized_suffixes = {suffix.lower() for suffix in suffixes}
    image_paths = sorted(
        path for path in dataset_path.rglob("*") if path.is_file() and path.suffix.lower() in normalized_suffixes
    )

    if not image_paths:
        raise FileNotFoundError(f"No raster images were found in: {dataset_path}")

    return image_paths


def load_raster_image(image_path: str | Path) -> np.ndarray:
    path = Path(image_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    with Image.open(path) as image:
        return np.array(image)


def collect_raster_image_summary_record(image_path: str | Path) -> dict[str, str]:
    path = Path(image_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    with Image.open(path) as image:
        pixel_array = np.array(image)
        image_format = image.format or ""
        image_mode = image.mode or ""

    return {
        "file_name": path.name,
        "image_path": str(path),
        "parent_dir": path.parent.name,
        "image_format": image_format,
        "image_mode": image_mode,
        "numpy_nrow": str(pixel_array.shape[0]) if pixel_array.ndim >= 1 else "",
        "numpy_ncol": str(pixel_array.shape[1]) if pixel_array.ndim >= 2 else "",
        "numpy_nchan": str(pixel_array.shape[2]) if pixel_array.ndim >= 3 else "",
        "numpy_max_value": str(np.max(pixel_array)),
        "pixel_array_shape": "x".join(str(dimension) for dimension in pixel_array.shape),
        "pixel_array_dtype": str(pixel_array.dtype),
    }


def export_image_summary_dataset(
    image_paths: list[str | Path],
    output_path: str | Path,
    fieldnames: tuple[str, ...] | list[str] = DEFAULT_IMAGE_SUMMARY_FIELDS,
    workers: int = 1,
) -> Path:
    if workers < 1:
        raise ValueError("workers must be at least 1")

    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(fieldnames))
        writer.writeheader()

        if workers == 1:
            for image_path in image_paths:
                record = collect_raster_image_summary_record(image_path)
                writer.writerow({field: record.get(field, "") for field in fieldnames})
        else:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {
                    executor.submit(collect_raster_image_summary_record, image_path): index
                    for index, image_path in enumerate(image_paths)
                }
                records_by_index: dict[int, dict[str, str]] = {}

                for future in as_completed(futures):
                    records_by_index[futures[future]] = future.result()

                for index in range(len(image_paths)):
                    record = records_by_index[index]
                    writer.writerow({field: record.get(field, "") for field in fieldnames})

    return destination