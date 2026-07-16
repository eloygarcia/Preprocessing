# metadata/factory.py

import json
import numpy as np
from pathlib import Path
from dataclasses import asdict

try:
    from ..models.metadata import (
        MammographyMetadata,
        PatientInfo,
        VendorInfo,
        AcquisitionInfo,
        BreastInfo,
        ImageInfo,
    )
    from ..extractors.patient import PatientExtractor
    from ..extractors.vendor import VendorExtractor
    from ..extractors.acquisition import AcquisitionExtractor
    from ..extractors.breast import BreastExtractor
    from ..extractors.image import ImageExtractor
    from ..processing.photometric import calculate_windowing
except ImportError:
    from models.metadata import (
        MammographyMetadata,
        PatientInfo,
        VendorInfo,
        AcquisitionInfo,
        BreastInfo,
        ImageInfo,
    )
    from extractors.patient import PatientExtractor
    from extractors.vendor import VendorExtractor
    from extractors.acquisition import AcquisitionExtractor
    from extractors.breast import BreastExtractor
    from extractors.image import ImageExtractor
    from processing.photometric import calculate_windowing


class MetadataFactory:
    PRESETS_FILE = Path(__file__).with_name("presets.json")

    @staticmethod
    def create(ds):
        return MammographyMetadata(
            patient=PatientExtractor.extract(ds),
            vendor=VendorExtractor.extract(ds),
            acquisition=AcquisitionExtractor.extract(ds),
            breast=BreastExtractor.extract(ds),
            image=ImageExtractor.extract(ds),
        )

    @staticmethod
    def _base_default_dict(pixel_array: np.ndarray | None = None):
        rows = None
        columns = None
        bits_stored = None
        window_center = None
        window_width = None

        if pixel_array is not None:
            rows, columns = pixel_array.shape[:2]

            if np.issubdtype(pixel_array.dtype, np.integer):
                bits_stored = np.iinfo(pixel_array.dtype).bits

            try:
                window_center, window_width = calculate_windowing(pixel_array)
            except Exception:
                pass

        return {
            "patient": {
                "patient_id": None,
                "age": None,
                "sex": None,
            },
            "vendor": {
                "manufacturer": None,
                "model_name": None,
            },
            "acquisition": {
                "kvp": None,
                "exposure": None,
                "exposure_time": None,
                "tube_current": None,
                "compression_force": None,
            },
            "breast": {
                "laterality": None,
                "view": None,
                "breast_implant_present": None,
            },
            "image": {
                "rows": rows,
                "columns": columns,
                "bits_stored": bits_stored,
                "pixel_spacing": None,
                "photometric_interpretation": "MONOCHROME2",
                "presentation_lut_shape": "IDENTITY",
                "window_center": window_center,
                "window_width": window_width,
                "window_center_width_explanation": "AUTO",
                "voi_lut_function": "LINEAR",
            },
        }

    @staticmethod
    def _deep_merge(base: dict, override: dict):
        merged = dict(base)

        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = MetadataFactory._deep_merge(merged[key], value)
            else:
                merged[key] = value

        return merged

    @staticmethod
    def _load_json_dict(file_path):
        with open(file_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _build_from_dict(data: dict):
        image_data = dict(data["image"])
        pixel_spacing = image_data.get("pixel_spacing")
        if isinstance(pixel_spacing, list):
            image_data["pixel_spacing"] = tuple(pixel_spacing)

        return MammographyMetadata(
            patient=PatientInfo(**data["patient"]),
            vendor=VendorInfo(**data["vendor"]),
            acquisition=AcquisitionInfo(**data["acquisition"]),
            breast=BreastInfo(**data["breast"]),
            image=ImageInfo(**image_data),
        )

    @staticmethod
    def to_dict(metadata: MammographyMetadata):
        return asdict(metadata)

    @staticmethod
    def create_default(pixel_array: np.ndarray | None = None, defaults: dict | None = None):
        metadata_dict = MetadataFactory._base_default_dict(pixel_array)
        if defaults is not None:
            metadata_dict = MetadataFactory._deep_merge(metadata_dict, defaults)
        return MetadataFactory._build_from_dict(metadata_dict)

    @staticmethod
    def refresh_image_metadata(
        metadata: MammographyMetadata | None,
        pixel_array: np.ndarray,
        image_overrides: dict | None = None,
    ):
        base_dict = MetadataFactory._base_default_dict(pixel_array)
        if metadata is not None:
            base_dict = MetadataFactory._deep_merge(
                base_dict,
                MetadataFactory.to_dict(metadata),
            )

        derived_image = MetadataFactory._base_default_dict(pixel_array)["image"]
        for field_name in ["rows", "columns", "bits_stored", "window_center", "window_width"]:
            base_dict["image"][field_name] = derived_image[field_name]

        if image_overrides is not None:
            base_dict["image"] = MetadataFactory._deep_merge(
                base_dict["image"],
                image_overrides,
            )

        return MetadataFactory._build_from_dict(base_dict)

    @staticmethod
    def create_from_dict(defaults: dict, pixel_array: np.ndarray | None = None):
        return MetadataFactory.create_default(pixel_array=pixel_array, defaults=defaults)

    @staticmethod
    def create_from_file(file_path, pixel_array: np.ndarray | None = None, preset_name: str | None = None):
        defaults = MetadataFactory._load_json_dict(file_path)

        metadata_sections = {"patient", "vendor", "acquisition", "breast", "image"}
        if preset_name is not None:
            return MetadataFactory.create_preset(
                preset_name,
                pixel_array=pixel_array,
                presets=defaults,
            )

        if not metadata_sections.intersection(defaults.keys()):
            raise ValueError(
                "The JSON file looks like a preset collection. Pass preset_name=... "
                "or use MetadataFactory.create_preset(...)."
            )

        return MetadataFactory.create_default(pixel_array=pixel_array, defaults=defaults)

    @staticmethod
    def create_preset(
        name: str,
        pixel_array: np.ndarray | None = None,
        presets: dict | None = None,
        presets_path=None,
        overrides: dict | None = None,
    ):
        if presets is None:
            presets_source = presets_path or MetadataFactory.PRESETS_FILE
            presets = MetadataFactory._load_json_dict(presets_source)

        preset_lookup = {key.lower(): value for key, value in presets.items()}
        preset = preset_lookup.get(name.lower())
        if preset is None:
            available = ", ".join(sorted(presets.keys()))
            raise KeyError(f"Unknown metadata preset '{name}'. Available presets: {available}")

        merged_defaults = preset
        if overrides is not None:
            merged_defaults = MetadataFactory._deep_merge(merged_defaults, overrides)

        return MetadataFactory.create_default(
            pixel_array=pixel_array,
            defaults=merged_defaults,
        )

    @staticmethod
    def create_default_from_array(pixel_array: np.ndarray):
        return MetadataFactory.create_default(pixel_array=pixel_array)
    
