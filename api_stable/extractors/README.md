# extractors

Extractores de tags DICOM hacia dataclasses tipadas.
Cada extractor lee un subconjunto de tags de un `pydicom.Dataset` y devuelve
el dataclass correspondiente de `models/metadata.py`.

## Principio de diseño

- Cada extractor es una clase con un único método estático `extract(ds)`.
- Usan `getattr(ds, tag, None)` y `ds.get(tag, None)` para acceso tolerante a fallos.
- No tienen estado ni efectos secundarios.
- No acceden a pixel data.

## Archivos

| Archivo | Clase | Dataclass producido |
|---|---|---|
| `patient.py` | `PatientExtractor` | `PatientInfo` |
| `vendor.py` | `VendorExtractor` | `VendorInfo` |
| `acquisition.py` | `AcquisitionExtractor` | `AcquisitionInfo` |
| `breast.py` | `BreastExtractor` | `BreastInfo` |
| `image.py` | `ImageExtractor` | `ImageInfo` |

---

## `PatientExtractor`

```python
PatientExtractor.extract(ds) -> PatientInfo
```

| Tag DICOM | Campo | Tratamiento especial |
|---|---|---|
| `PatientID` | `patient_id` | — |
| `PatientAge` | `age` | Extrae solo dígitos (`044Y` → `44`) |
| `PatientSex` | `sex` | — |

---

## `VendorExtractor`

```python
VendorExtractor.extract(ds) -> VendorInfo
```

| Tag DICOM | Campo |
|---|---|
| `Manufacturer` | `manufacturer` |
| `ManufacturerModelName` | `model_name` |

---

## `AcquisitionExtractor`

```python
AcquisitionExtractor.extract(ds) -> AcquisitionInfo
```

| Tag DICOM | Campo |
|---|---|
| `KVP` | `kvp` |
| `Exposure` | `exposure` |
| `ExposureTime` | `exposure_time` |
| `XRayTubeCurrent` | `tube_current` |
| `CompressionForce` | `compression_force` |

---

## `BreastExtractor`

```python
BreastExtractor.extract(ds) -> BreastInfo
```

| Tag DICOM | Campo | Tratamiento especial |
|---|---|---|
| `ImageLaterality` / `Laterality` | `laterality` | Fallback entre ambos tags |
| `ViewPosition` | `view` | — |
| `BreastImplantPresent` | `breast_implant_present` | `"YES"/"Y"/"TRUE"/"1"` → `True` |

---

## `ImageExtractor`

```python
ImageExtractor.extract(ds) -> ImageInfo
```

| Tag DICOM | Campo | Tratamiento especial |
|---|---|---|
| `Rows` | `rows` | — |
| `Columns` | `columns` | — |
| `BitsStored` | `bits_stored` | — |
| `PixelSpacing` | `pixel_spacing` | Convertido a `tuple[float, float]` |
| `PhotometricInterpretation` | `photometric_interpretation` | — |
| `PresentationLUTShape` | `presentation_lut_shape` | — |
| `WindowCenter` | `window_center` | Puede ser `MultiValue` (varios preset de ventana) |
| `WindowWidth` | `window_width` | Puede ser `MultiValue` |
| `WindowCenterWidthExplanation` | `window_center_width_explanation` | `NORMAL`, `HARDER`, `SOFTER` |
| `VOILUTFunction` | `voi_lut_function` | `LINEAR`, `SIGMOID` |

---

## Uso directo

En condiciones normales los extractores se invocan a través de `MetadataFactory.create(ds)`.
Si necesitas solo un subconjunto:

```python
import pydicom
from api_stable.extractors.vendor import VendorExtractor

ds = pydicom.dcmread("archivo.dcm")
vendor = VendorExtractor.extract(ds)
print(vendor.manufacturer, vendor.model_name)
```
