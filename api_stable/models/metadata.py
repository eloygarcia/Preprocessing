import numpy as np
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel

class View(Enum):
    LCC = "LCC"
    RCC = "RCC"
    LMLO = "LMLO"
    RMLO = "RMLO"

class PatientInfo(BaseModel):
    patient_id: str | None
    age: int | None
    sex: str | None

class VendorInfo(BaseModel):
    manufacturer: str | None
    model_name: str | None
    #software_version: str | None

class AcquisitionInfo(BaseModel):
    kvp: float | None
    exposure: float | None
    exposure_time: float | None
    tube_current: float | None
    compression_force: float | None

class BreastInfo(BaseModel):
    laterality: str | None
    view: str | None
    breast_implant_present: bool | None

class ImageInfo(BaseModel):
    rows: int
    columns: int
    bits_stored: int
    pixel_spacing: tuple[float,float] | None
    photometric_interpretation: str | None # MONOCHROME1\MONOCHROME2
    presentation_lut_shape: str | None # IDENTITY\INVERSE
    window_center: list | None
    window_width: list | None
    window_center_width_explanation: list | None  # NORMAL\HARDER\SOFTER
    voi_lut_function: str | None

class MammographyMetadata(BaseModel):
    patient: PatientInfo
    vendor: VendorInfo
    acquisition: AcquisitionInfo
    breast: BreastInfo
    image: ImageInfo
