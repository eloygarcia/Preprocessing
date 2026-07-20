import numpy as np
from enum import Enum
from dataclasses import dataclass

class View(Enum):
    LCC = "LCC"
    RCC = "RCC"
    LMLO = "LMLO"
    RMLO = "RMLO"

@dataclass
class PatientInfo:
    patient_id: str | None
    age: int | None
    sex: str | None

@dataclass
class VendorInfo:
    manufacturer: str | None
    model_name: str | None
    #software_version: str | None

@dataclass
class AcquisitionInfo:
    kvp: float | None
    exposure: float | None
    exposure_time: float | None
    tube_current: float | None
    compression_force: float | None

@dataclass
class BreastInfo:
    laterality: str | None
    view: str | None
    breast_implant_present: bool | None

@dataclass
class ImageInfo:
    rows: int
    columns: int
    bits_stored: int
    pixel_spacing: tuple[float,float] | None
    photometric_interpretation: str | None # MONOCHROME1\MONOCHROME2
    presentation_lut_shape: str | None # IDENTITY\INVERSE
    window_center: float | None
    window_width: float | None
    window_center_width_explanation: str | None  # NORMAL\HARDER\SOFTER
    voi_lut_function: str | None

@dataclass
class MammographyMetadata:
    patient: PatientInfo
    vendor: VendorInfo
    acquisition: AcquisitionInfo
    breast: BreastInfo
    image: ImageInfo
