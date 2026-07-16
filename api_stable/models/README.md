# models

Dataclasses tipadas que representan el estado de una mamografía.
No contienen lógica de negocio ni dependencias de DICOM.

## Archivos

| Archivo | Contenido |
|---|---|
| `metadata.py` | Jerarquía completa de dataclasses para metadata |
| `image.py` | `MammographyImage`: contenedor de pixel array con historial de transformaciones |

---

## `metadata.py` — Modelos de metadata

Todas las clases son `@dataclass`. Los campos opcionales usan `... | None`.

### `PatientInfo`
Información demográfica del paciente.

| Campo | Tipo | Tag DICOM |
|---|---|---|
| `patient_id` | `str \| None` | `PatientID` |
| `age` | `int \| None` | `PatientAge` (parseo de formato `044Y`) |
| `sex` | `str \| None` | `PatientSex` |

### `VendorInfo`
Identificación del equipo de adquisición.

| Campo | Tipo | Tag DICOM |
|---|---|---|
| `manufacturer` | `str \| None` | `Manufacturer` |
| `model_name` | `str \| None` | `ManufacturerModelName` |

### `AcquisitionInfo`
Parámetros físicos de adquisición.

| Campo | Tipo | Tag DICOM |
|---|---|---|
| `kvp` | `float \| None` | `KVP` |
| `exposure` | `float \| None` | `Exposure` |
| `exposure_time` | `float \| None` | `ExposureTime` |
| `tube_current` | `float \| None` | `XRayTubeCurrent` |
| `compression_force` | `float \| None` | `CompressionForce` |

### `BreastInfo`
Información de lateralidad y proyección.

| Campo | Tipo | Tag DICOM |
|---|---|---|
| `laterality` | `str \| None` | `ImageLaterality` / `Laterality` |
| `view` | `str \| None` | `ViewPosition` |
| `breast_implant_present` | `bool \| None` | `BreastImplantPresent` |

### `ImageInfo`
Parámetros de imagen y visualización.

| Campo | Tipo | Tag DICOM | Valores típicos |
|---|---|---|---|
| `rows` | `int` | `Rows` | — |
| `columns` | `int` | `Columns` | — |
| `bits_stored` | `int` | `BitsStored` | 8, 12, 16 |
| `pixel_spacing` | `tuple[float,float] \| None` | `PixelSpacing` | — |
| `photometric_interpretation` | `str \| None` | `PhotometricInterpretation` | `MONOCHROME1`, `MONOCHROME2` |
| `presentation_lut_shape` | `str \| None` | `PresentationLUTShape` | `IDENTITY`, `INVERSE` |
| `window_center` | `float \| None` | `WindowCenter` | — |
| `window_width` | `float \| None` | `WindowWidth` | — |
| `window_center_width_explanation` | `str \| None` | `WindowCenterWidthExplanation` | `NORMAL`, `HARDER`, `SOFTER`, `AUTO`, `APPLIED`, `NORMALIZED` |
| `voi_lut_function` | `str \| None` | `VOILUTFunction` | `LINEAR`, `SIGMOID` |

### `MammographyMetadata`
Contenedor raíz que agrupa todos los bloques anteriores.

```python
@dataclass
class MammographyMetadata:
    patient:     PatientInfo
    vendor:      VendorInfo
    acquisition: AcquisitionInfo
    breast:      BreastInfo
    image:       ImageInfo
```

---

## `image.py` — MammographyImage

Contenedor de pixel array con operaciones encadenables.
**No tiene dependencia de DICOM**: todos los parámetros se reciben explícitamente.

### Propiedades de solo lectura

| Propiedad | Descripción |
|---|---|
| `pixel_array` | Array numpy actual |
| `shape` | Dimensiones `(rows, columns)` |
| `dtype` | Tipo de dato numpy |
| `min` | Valor mínimo del array actual |
| `max` | Valor máximo del array actual |

### Métodos

| Método | Parámetros | Descripción |
|---|---|---|
| `normalize()` | — | Normalización min-max al rango [0, 1] |
| `convert_to_monochrome2()` | — | Inversión de intensidades (`max - arr`) para MONOCHROME1 |
| `apply_windowing(window_center, window_width, voi_lut_function, backend)` | opcionales | Aplica windowing VOI LUT. Si no se pasan parámetros, los estima desde el histograma |
| `copy()` | — | Copia profunda independiente del objeto |
| `to_numpy()` | — | Devuelve el array numpy actual |
| `get_history()` | — | Lista de strings con las transformaciones aplicadas |

### Atributos de estado

| Atributo | Descripción |
|---|---|
| `history` | Lista de strings de transformaciones aplicadas |
| `last_windowing` | Dict con `window_center`, `window_width`, `voi_lut_function` de la última llamada a `apply_windowing` |

### Ejemplo

```python
from api_stable.models.image import MammographyImage

img = MammographyImage(pixel_array)
img.convert_to_monochrome2().apply_windowing(window_center=1500, window_width=3000).normalize()
print(img.get_history())
# ['convert_to_monochrome2', 'apply_windowing(...)', 'normalize']
```

> Las operaciones que dependen de metadata DICOM (fotometría, windowing desde tags)
> las resuelve `MammographyDicom` en `mammography.py` y las pasa como parámetros explícitos.
