from pathlib import Path
from typing import Any
import csv
import re

import numpy as np
import pydicom
from pydicom.dataset import Dataset
from pydicom.multival import MultiValue
from pydicom.sequence import Sequence
from PIL import Image
from scipy import ndimage as ndi
from skimage.measure import label, regionprops
from skimage.morphology import closing, disk


DEFAULT_METADATA_FIELDS = (
    "PatientID",
    "StudyDate",
    "Modality",
    "Manufacturer",
    "Rows",
    "Columns",
    "BitsStored",
    "PhotometricInterpretation",
    "PixelSpacing",
    "ViewPosition",
    "ImageLaterality",
    "WindowCenter",
    "WindowWidth",
    "RescaleIntercept",
    "RescaleSlope",
)

DEFAULT_PECTORAL_MASKS_DIR = Path("~/Escritorio/Datasets/InBreast/pectoral_masks").expanduser()
DEFAULT_WHOLE_BREAST_MASKS_DIR = Path("~/Escritorio/Datasets/InBreast/whole_breast_mask").expanduser()
DEFAULT_METADATA_DATASET_PATH = Path("~/Escritorio/Datasets/InBreast/inbreast_image_metadata.csv").expanduser()

DEFAULT_METADATA_EXPORT_FIELDS = (
    "file_name",
    "image_path",
    "image_id",
    "case_id",
    "laterality",
    "view_position",
    "is_mlo",
    "has_pectoral_mask",
    "manufacturer",
    "manufacturer_model_name",
    "modality",
    "presentation_intent_type",
    "study_date",
    "patient_id",
    "body_part_examined",
    "photometric_interpretation",
    "rows",
    "columns",
    "samples_per_pixel",
    "bits_allocated",
    "bits_stored",
    "high_bit",
    "pixel_representation",
    "pixel_spacing",
    "pixel_size_row_mm",
    "pixel_size_col_mm",
    "imager_pixel_spacing",
    "voi_lut_function",
    "voi_lut_sequence_present",
    "voi_lut_sequence_length",
    "voi_lut_explanation",
    "window_center",
    "window_width",
    "windowing_available",
    "windowing_source",
    "rescale_intercept",
    "rescale_slope",
    "study_instance_uid",
    "series_instance_uid",
    "sop_instance_uid",
    "transfer_syntax_uid",
)

DEFAULT_DICOM_TAG_EXPORT_PATH = Path("~/Escritorio/Datasets/InBreast/inbreast_dicom_tags.csv").expanduser()

DEFAULT_DICOM_TAG_SUMMARY_FIELDS = (
    "file_name",
    "image_path",
    "tag_count",
    "numpy_nrow",
    "numpy_ncol",
    "numpy_max_value",
    "rows_match",
    "cols_match",
    "max_match",
    "pixel_array_shape",
    "pixel_array_dtype",
    "pixel_array_max",
)


def _coerce_metadata_value(value: Any):
    if isinstance(value, MultiValue):
        return [_coerce_metadata_value(item) for item in value]

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, bytes):
        return value.decode(errors="ignore")

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool, list, dict)):
        return value

    return str(value)


def _compact_metadata_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def _stringify_dataset_value(dataset: Dataset) -> str:
    entries = []

    for data_element in dataset:
        if data_element.tag == 0x7FE00010:
            continue

        keyword = data_element.keyword or _normalize_tag_label(data_element.name)
        value = _stringify_metadata_value(data_element.value)
        if value:
            entries.append(f"{keyword}={value}")

    return " | ".join(entries)


def _stringify_metadata_value(value: Any) -> str:
    if isinstance(value, Dataset):
        return _stringify_dataset_value(value)

    if isinstance(value, Sequence):
        return " || ".join(_stringify_dataset_value(item) for item in value)

    coerced_value = _coerce_metadata_value(value)

    if coerced_value is None:
        return ""

    if isinstance(coerced_value, list):
        return "|".join(_compact_metadata_text(item) for item in coerced_value)

    if isinstance(coerced_value, dict):
        return " | ".join(
            f"{key}={_compact_metadata_text(item)}"
            for key, item in coerced_value.items()
        )

    return _compact_metadata_text(coerced_value)


def _normalize_tag_label(label: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z]+", "_", label).strip("_").lower()
    return normalized or "unknown"


def _build_tag_column_name(data_element: pydicom.DataElement, prefix: str = "tag") -> str:
    keyword = data_element.keyword or data_element.name
    return f"{prefix}_{data_element.tag.group:04x}_{data_element.tag.element:04x}_{_normalize_tag_label(keyword)}"


def _collect_dataset_tag_values(
    dataset: pydicom.Dataset,
    include_file_meta: bool = True,
    include_private_tags: bool = False,
) -> dict[str, str]:
    tag_values: dict[str, str] = {}

    for data_element in dataset:
        if data_element.tag == 0x7FE00010:
            continue
        if data_element.tag.is_private and not include_private_tags:
            continue

        tag_values[_build_tag_column_name(data_element)] = _stringify_metadata_value(data_element.value)

    if include_file_meta:
        for data_element in getattr(dataset, "file_meta", []):
            if data_element.tag.is_private and not include_private_tags:
                continue

            tag_values[_build_tag_column_name(data_element, prefix="file_meta")] = _stringify_metadata_value(data_element.value)

    return tag_values


def _values_match(first_value: Any, second_value: Any) -> str:
    if first_value in (None, "") or second_value in (None, ""):
        return ""

    try:
        return str(float(first_value) == float(second_value))
    except (TypeError, ValueError):
        return str(str(first_value) == str(second_value))


def _summarize_pixel_array(dataset: pydicom.Dataset) -> dict[str, str]:
    image = dataset.pixel_array
    numpy_nrow = str(image.shape[0]) if image.ndim >= 1 else ""
    numpy_ncol = str(image.shape[1]) if image.ndim >= 2 else ""
    numpy_max_value = _stringify_metadata_value(np.max(image))
    rows_tag_value = _stringify_metadata_value(getattr(dataset, "Rows", None))
    cols_tag_value = _stringify_metadata_value(getattr(dataset, "Columns", None))
    largest_pixel_tag_value = _stringify_metadata_value(getattr(dataset, "LargestImagePixelValue", None))

    return {
        "numpy_nrow": numpy_nrow,
        "numpy_ncol": numpy_ncol,
        "numpy_max_value": numpy_max_value,
        "rows_match": _values_match(rows_tag_value, numpy_nrow),
        "cols_match": _values_match(cols_tag_value, numpy_ncol),
        "max_match": _values_match(largest_pixel_tag_value, numpy_max_value),
        "pixel_array_shape": "x".join(str(dimension) for dimension in image.shape),
        "pixel_array_dtype": str(image.dtype),
        "pixel_array_max": numpy_max_value,
    }


def _parse_filename_metadata(image_path: str | Path) -> dict[str, Any]:
    dicom_path = Path(image_path).expanduser()
    parts = dicom_path.stem.split("_")

    if len(parts) < 5:
        raise ValueError(f"Unexpected INBreast file name format: {dicom_path.name}")

    return {
        "image_id": parts[0],
        "case_id": parts[1],
        "laterality": parts[3],
        "view_position": parts[4],
        "is_mlo": parts[4] == "ML",
    }


def _extract_pixel_spacing(dataset: pydicom.Dataset) -> tuple[str, str, str]:
    pixel_spacing = getattr(dataset, "PixelSpacing", None)
    imager_pixel_spacing = getattr(dataset, "ImagerPixelSpacing", None)
    spacing_source = pixel_spacing if pixel_spacing is not None else imager_pixel_spacing

    if spacing_source and len(spacing_source) >= 2:
        return (
            _stringify_metadata_value(pixel_spacing),
            str(_coerce_metadata_value(spacing_source[0])),
            str(_coerce_metadata_value(spacing_source[1])),
        )

    return (
        _stringify_metadata_value(pixel_spacing),
        "",
        "",
    )


def _extract_voi_lut_metadata(dataset: pydicom.Dataset) -> dict[str, Any]:
    voi_lut_sequence = getattr(dataset, "VOILUTSequence", None)
    voi_lut_explanation = getattr(dataset, "VOILUTExplanation", None)

    return {
        "voi_lut_function": _stringify_metadata_value(getattr(dataset, "VOILUTFunction", None)),
        "voi_lut_sequence_present": bool(voi_lut_sequence),
        "voi_lut_sequence_length": len(voi_lut_sequence) if voi_lut_sequence else 0,
        "voi_lut_explanation": _stringify_metadata_value(voi_lut_explanation),
    }


def _extract_windowing_metadata(dataset: pydicom.Dataset) -> dict[str, Any]:
    window_center = _stringify_metadata_value(getattr(dataset, "WindowCenter", None))
    window_width = _stringify_metadata_value(getattr(dataset, "WindowWidth", None))
    voi_lut_function = _stringify_metadata_value(getattr(dataset, "VOILUTFunction", None))

    if window_center and window_width:
        windowing_source = "dicom_window"
    elif voi_lut_function:
        windowing_source = "voi_lut_function"
    else:
        windowing_source = "not_available"

    return {
        "window_center": window_center,
        "window_width": window_width,
        "windowing_available": bool(window_center and window_width),
        "windowing_source": windowing_source,
    }


def _normalize_to_unit_interval(image: np.ndarray) -> np.ndarray:
    normalized = image.astype(np.float32, copy=True)
    normalized -= normalized.min()
    max_value = normalized.max()
    if max_value > 0:
        normalized /= max_value
    return normalized


def _prepare_mammogram_pixels(dataset: pydicom.Dataset) -> np.ndarray:
    image = dataset.pixel_array.astype(np.float32)

    if getattr(dataset, "PhotometricInterpretation", "") == "MONOCHROME1":
        image = image.max() - image

    return image


def read_dicom_metadata(
    image_path: str | Path,
    fields: tuple[str, ...] | list[str] = DEFAULT_METADATA_FIELDS,
) -> dict[str, Any]:
    dicom_path = Path(image_path).expanduser()
    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    dataset = pydicom.dcmread(dicom_path, stop_before_pixels=True)
    metadata = {"image_path": str(dicom_path), "file_name": dicom_path.name}

    for field in fields:
        metadata[field] = _coerce_metadata_value(getattr(dataset, field, None))

    return metadata


def collect_dicom_metadata_record(
    image_path: str | Path,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
) -> dict[str, Any]:
    dicom_path = Path(image_path).expanduser()
    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    filename_metadata = _parse_filename_metadata(dicom_path)
    dataset = pydicom.dcmread(dicom_path, stop_before_pixels=True)
    pixel_spacing, pixel_size_row_mm, pixel_size_col_mm = _extract_pixel_spacing(dataset)
    voi_lut_metadata = _extract_voi_lut_metadata(dataset)
    windowing_metadata = _extract_windowing_metadata(dataset)

    try:
        has_pectoral_mask = get_pectoral_mask_path(dicom_path, masks_dir=masks_dir).exists()
    except (FileNotFoundError, ValueError):
        has_pectoral_mask = False

    return {
        "file_name": dicom_path.name,
        "image_path": str(dicom_path),
        "image_id": filename_metadata["image_id"],
        "case_id": filename_metadata["case_id"],
        "laterality": filename_metadata["laterality"],
        "view_position": filename_metadata["view_position"],
        "is_mlo": filename_metadata["is_mlo"],
        "has_pectoral_mask": has_pectoral_mask,
        "manufacturer": _stringify_metadata_value(getattr(dataset, "Manufacturer", None)),
        "manufacturer_model_name": _stringify_metadata_value(getattr(dataset, "ManufacturerModelName", None)),
        "modality": _stringify_metadata_value(getattr(dataset, "Modality", None)),
        "presentation_intent_type": _stringify_metadata_value(getattr(dataset, "PresentationIntentType", None)),
        "study_date": _stringify_metadata_value(getattr(dataset, "StudyDate", None)),
        "patient_id": _stringify_metadata_value(getattr(dataset, "PatientID", None)),
        "body_part_examined": _stringify_metadata_value(getattr(dataset, "BodyPartExamined", None)),
        "photometric_interpretation": _stringify_metadata_value(getattr(dataset, "PhotometricInterpretation", None)),
        "rows": _stringify_metadata_value(getattr(dataset, "Rows", None)),
        "columns": _stringify_metadata_value(getattr(dataset, "Columns", None)),
        "samples_per_pixel": _stringify_metadata_value(getattr(dataset, "SamplesPerPixel", None)),
        "bits_allocated": _stringify_metadata_value(getattr(dataset, "BitsAllocated", None)),
        "bits_stored": _stringify_metadata_value(getattr(dataset, "BitsStored", None)),
        "high_bit": _stringify_metadata_value(getattr(dataset, "HighBit", None)),
        "pixel_representation": _stringify_metadata_value(getattr(dataset, "PixelRepresentation", None)),
        "pixel_spacing": pixel_spacing,
        "pixel_size_row_mm": pixel_size_row_mm,
        "pixel_size_col_mm": pixel_size_col_mm,
        "imager_pixel_spacing": _stringify_metadata_value(getattr(dataset, "ImagerPixelSpacing", None)),
        "rescale_intercept": _stringify_metadata_value(getattr(dataset, "RescaleIntercept", None)),
        "rescale_slope": _stringify_metadata_value(getattr(dataset, "RescaleSlope", None)),
        "study_instance_uid": _stringify_metadata_value(getattr(dataset, "StudyInstanceUID", None)),
        "series_instance_uid": _stringify_metadata_value(getattr(dataset, "SeriesInstanceUID", None)),
        "sop_instance_uid": _stringify_metadata_value(getattr(dataset, "SOPInstanceUID", None)),
        "transfer_syntax_uid": _stringify_metadata_value(getattr(getattr(dataset, "file_meta", None), "TransferSyntaxUID", None)),
        **voi_lut_metadata,
        **windowing_metadata,
    }


def collect_dicom_tag_record(
    image_path: str | Path,
    include_pixel_summary: bool = True,
    include_file_meta: bool = True,
    include_private_tags: bool = False,
) -> dict[str, str]:
    dicom_path = Path(image_path).expanduser()
    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    dataset = pydicom.dcmread(dicom_path)
    tag_values = _collect_dataset_tag_values(
        dataset,
        include_file_meta=include_file_meta,
        include_private_tags=include_private_tags,
    )

    record = {
        "file_name": dicom_path.name,
        "image_path": str(dicom_path),
        "tag_count": str(len(tag_values)),
    }

    if include_pixel_summary:
        record.update(_summarize_pixel_array(dataset))

    record.update(tag_values)
    return record


def export_dicom_tag_dataset(
    image_paths: list[str | Path],
    output_path: str | Path = DEFAULT_DICOM_TAG_EXPORT_PATH,
    include_pixel_summary: bool = True,
    include_file_meta: bool = True,
    include_private_tags: bool = False,
    base_fieldnames: tuple[str, ...] | list[str] = DEFAULT_DICOM_TAG_SUMMARY_FIELDS,
    delimiter: str = ";",
) -> Path:
    records = [
        collect_dicom_tag_record(
            image_path,
            include_pixel_summary=include_pixel_summary,
            include_file_meta=include_file_meta,
            include_private_tags=include_private_tags,
        )
        for image_path in image_paths
    ]

    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    ordered_fieldnames = [field for field in base_fieldnames if any(field in record for record in records)]
    dynamic_fieldnames = sorted(
        {
            key
            for record in records
            for key in record
            if key not in ordered_fieldnames
        }
    )
    fieldnames = ordered_fieldnames + dynamic_fieldnames

    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()

        for record in records:
            writer.writerow({field: record.get(field, "") for field in fieldnames})

    return destination


def export_metadata_dataset(
    image_paths: list[str | Path],
    output_path: str | Path = DEFAULT_METADATA_DATASET_PATH,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
    fieldnames: tuple[str, ...] | list[str] = DEFAULT_METADATA_EXPORT_FIELDS,
) -> Path:
    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(fieldnames))
        writer.writeheader()

        for image_path in image_paths:
            record = collect_dicom_metadata_record(image_path, masks_dir=masks_dir)
            writer.writerow({field: record.get(field, "") for field in fieldnames})

    return destination


def load_dicom_pixels(image_path: str | Path, normalize: bool = False) -> np.ndarray:
    dicom_path = Path(image_path).expanduser()
    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    dataset = pydicom.dcmread(dicom_path)
    image = _prepare_mammogram_pixels(dataset)

    if normalize:
        return _normalize_to_unit_interval(image)

    return image


def segment_breast_region(
    image: np.ndarray,
    threshold: float = 0.0,
    closing_radius: int = 5,
    fill_holes: bool = True,
) -> np.ndarray:
    image_array = np.asarray(image, dtype=np.float32)

    if image_array.ndim != 2:
        raise ValueError("segment_breast_region expects a 2D image")

    mask = image_array > threshold
    if closing_radius > 0:
        mask = closing(mask, footprint=disk(closing_radius))

    labels = label(mask)
    if labels.max() == 0:
        return mask.astype(bool)

    largest_region = max(regionprops(labels), key=lambda region: region.area)
    breast_mask = labels == largest_region.label

    if fill_holes:
        breast_mask = ndi.binary_fill_holes(breast_mask)

    return breast_mask.astype(bool)


def apply_background_mask(
    image: np.ndarray,
    mask: np.ndarray,
    background_value: float = 0.0,
) -> np.ndarray:
    image_array = np.asarray(image, dtype=np.float32)
    mask_array = np.asarray(mask, dtype=bool)

    if image_array.shape != mask_array.shape:
        raise ValueError("image and mask must have the same shape")

    masked_image = image_array.copy()
    masked_image[~mask_array] = background_value

    return masked_image


def convert_dicom_to_uint8_png(
    image_path: str | Path,
    output_path: str | Path,
    use_windowing: bool = False,
) -> Path:
    image = load_dicom_pixels(image_path, normalize=not use_windowing)
    if use_windowing:
        image = apply_windowing(image) ## Check before continue

    image_uint8 = np.clip(np.rint(image * 255.0), 0, 255).astype(np.uint8)
    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image_uint8, mode="L").save(destination)

    return destination


def get_dicom_png_output_path(
    image_path: str | Path,
    dataset_root: str | Path,
    output_root: str | Path,
) -> Path:
    source_path = Path(image_path).expanduser()
    source_root = Path(dataset_root).expanduser().resolve()
    destination_root = Path(output_root).expanduser()

    relative_path = source_path.resolve().relative_to(source_root)
    return destination_root / relative_path.with_suffix(".png")


def get_pectoral_mask_path(
    image_path: str | Path,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
) -> Path:
    dicom_path = Path(image_path).expanduser()
    masks_path = Path(masks_dir).expanduser()

    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    if "_MG_" not in dicom_path.name or "_ML_" not in dicom_path.name:
        raise ValueError("Pectoral masks are only available for MLO images")

    image_id = dicom_path.name.split("_", maxsplit=1)[0]
    mask_path = masks_path / f"{image_id}_mask.png"

    if not mask_path.exists():
        raise FileNotFoundError(f"Pectoral mask not found: {mask_path}")

    return mask_path


def load_pectoral_mask(
    image_path: str | Path,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
) -> np.ndarray:
    mask_path = get_pectoral_mask_path(image_path, masks_dir=masks_dir)
    mask = np.array(Image.open(mask_path)) > 0

    return mask.astype(bool)


def create_mlo_labeled_mask(
    image_path: str | Path,
    breast_mask: np.ndarray | None = None,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
    breast_label: int = 1,
    pectoral_label: int = 2,
) -> np.ndarray:
    image = load_dicom_pixels(image_path)
    if breast_mask is None:
        breast_mask = segment_breast_region(apply_windowing(image))

    breast_mask_array = np.asarray(breast_mask, dtype=bool)
    pectoral_mask = load_pectoral_mask(image_path, masks_dir=masks_dir)

    if breast_mask_array.shape != pectoral_mask.shape:
        raise ValueError("breast mask and pectoral mask must have the same shape")

    labeled_mask = np.zeros(breast_mask_array.shape, dtype=np.uint8)
    labeled_mask[breast_mask_array] = breast_label
    labeled_mask[pectoral_mask] = pectoral_label

    return labeled_mask


def create_labeled_mask(
    image_path: str | Path,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
    breast_label: int = 1,
    pectoral_label: int = 2,
) -> np.ndarray:
    image = load_dicom_pixels(image_path)
    breast_mask = segment_breast_region(apply_windowing(image))

    labeled_mask = np.zeros(breast_mask.shape, dtype=np.uint8)
    labeled_mask[breast_mask] = breast_label

    try:
        pectoral_mask = load_pectoral_mask(image_path, masks_dir=masks_dir)
    except (FileNotFoundError, ValueError):
        pectoral_mask = None

    if pectoral_mask is not None:
        if pectoral_mask.shape != labeled_mask.shape:
            raise ValueError("pectoral mask and labeled mask must have the same shape")

        labeled_mask[pectoral_mask] = pectoral_label

    return labeled_mask


def get_labeled_mask_output_path(
    image_path: str | Path,
    output_dir: str | Path = DEFAULT_WHOLE_BREAST_MASKS_DIR,
) -> Path:
    dicom_path = Path(image_path).expanduser()
    output_path = Path(output_dir).expanduser()

    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    output_path.mkdir(parents=True, exist_ok=True)

    return output_path / f"{dicom_path.stem}.png"


def save_labeled_mask(
    image_path: str | Path,
    output_dir: str | Path = DEFAULT_WHOLE_BREAST_MASKS_DIR,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
) -> Path:
    labeled_mask = create_labeled_mask(image_path, masks_dir=masks_dir)
    output_path = get_labeled_mask_output_path(image_path, output_dir=output_dir)

    Image.fromarray(labeled_mask, mode="L").save(output_path)

    return output_path


def save_dataset_labeled_masks(
    image_paths: list[str | Path],
    output_dir: str | Path = DEFAULT_WHOLE_BREAST_MASKS_DIR,
    masks_dir: str | Path = DEFAULT_PECTORAL_MASKS_DIR,
) -> list[Path]:
    saved_paths = []

    for image_path in image_paths:
        saved_paths.append(
            save_labeled_mask(
                image_path,
                output_dir=output_dir,
                masks_dir=masks_dir,
            )
        )

    return saved_paths