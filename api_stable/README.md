# api_stable

API estable para carga, extraccion de metadatos y preprocesado de imagenes de mamografia DICOM y PNG.

## Arquitectura

```text
MammographyDicom
       │
       ├── metadata  →  MammographyMetadata
       │                  ├── PatientInfo
       │                  ├── VendorInfo
       │                  ├── AcquisitionInfo
       │                  ├── BreastInfo
       │                  └── ImageInfo
       │
       └── image     →  MammographyImage
```

## Estructura de carpetas

```text
api_stable/
├── mammography.py          ← punto de entrada: MammographyDicom
├── models/                 ← ver models/README.md
│   ├── metadata.py         ← dataclasses tipadas (PatientInfo, VendorInfo, ...)
│   └── image.py            ← MammographyImage (operaciones puras sobre píxeles)
├── extractors/             ← ver extractors/README.md
│   ├── patient.py
│   ├── vendor.py
│   ├── acquisition.py
│   ├── breast.py
│   └── image.py
├── metadata/               ← ver metadata/README.md
│   ├── factory.py          ← MetadataFactory (DICOM, preset, dict, file, refresh)
│   ├── presets.json        ← presets de fabricante (Hologic, GE, Siemens, ...)
│   └── build.py
└── processing/             ← ver processing/README.md
    ├── photometric.py      ← normalize_image, calculate_windowing, apply_windowing
    └── apply_windowing.py  ← implementaciones internas np_v1 / np_v2
```

### Documentación por subcarpeta

| Carpeta | Descripción | README |
|---|---|---|
| `models/` | Dataclasses tipadas + `MammographyImage` | [models/README.md](models/README.md) |
| `extractors/` | Lectura de tags DICOM a dataclasses | [extractors/README.md](extractors/README.md) |
| `metadata/` | `MetadataFactory`, presets, merge y refresco | [metadata/README.md](metadata/README.md) |
| `processing/` | Funciones puras: normalize, windowing | [processing/README.md](processing/README.md) |

## Uso básico

### Cargar DICOM

```python
from api_stable.mammography import MammographyDicom

mammo = MammographyDicom.from_dicom("ruta/al/archivo.dcm")
print(mammo.metadata)
print(mammo.image.shape)
```

### Cargar PNG con preset de fabricante

```python
mammo = MammographyDicom.from_png(
    "ruta/imagen.png",
    metadata_preset="Hologic",
    metadata_overrides={"breast": {"laterality": "R", "view": "MLO"}},
)
```

### Pipeline de preprocesado

```python
mammo.initialize_image()   # MONOCHROME1→2 + windowing (parámetros desde metadata)
mammo.normalize()          # normalización [0, 1]

print(mammo.image.get_history())
print(mammo.metadata.image)
```

### Inicializar metadata desde diccionario o archivo

```python
from api_stable.metadata.factory import MetadataFactory

# Desde preset
md = MetadataFactory.create_preset("GE", pixel_array=arr)

# Desde diccionario
md = MetadataFactory.create_from_dict(
    {"vendor": {"manufacturer": "ACME", "model_name": "X"}},
    pixel_array=arr,
)

# Desde archivo JSON
md = MetadataFactory.create_from_file("mi_defaults.json", pixel_array=arr)

# Desde archivo de presets
md = MetadataFactory.create_from_file(
    "api_stable/metadata/presets.json",
    pixel_array=arr,
    preset_name="Hologic",
)
```

## Principios de diseño

| Capa | Responsabilidad |
|---|---|
| `processing/` | Funciones puras: solo arrays numpy y parámetros numéricos |
| `extractors/` | Lectura y tipado de tags DICOM |
| `metadata/factory.py` | Construcción y refresco de `MammographyMetadata` |
| `models/image.py` | Estado + historial de transformaciones de la imagen |
| `mammography.py` | Orquestación: resuelve metadatos y delega en el modelo |

## Presets disponibles

Los presets se definen en `metadata/presets.json`.
Actualmente: `Hologic`, `GE`, `Siemens`.

Para añadir un nuevo preset, edita el JSON con la estructura:

```json
"NombrePreset": {
  "vendor": { "manufacturer": "...", "model_name": "..." },
  "image": { "photometric_interpretation": "MONOCHROME2", "voi_lut_function": "LINEAR" }
}
```