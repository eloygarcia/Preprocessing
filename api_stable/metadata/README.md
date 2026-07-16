# metadata

Construcción y gestión de objetos `MammographyMetadata`.
Cubre tres fuentes de datos: DICOM, preset de fabricante y valores por defecto desde array numpy.

## Archivos

| Archivo | Descripción |
|---|---|
| `factory.py` | `MetadataFactory`: todos los constructores y la lógica de merge |
| `presets.json` | Presets predefinidos por fabricante |
| `build.py` | Función `build_metadata(ds)` — interfaz simplificada (wrapper de factory) |

---

## `MetadataFactory`

Clase con métodos estáticos. No tiene estado.

### Constructores

#### Desde DICOM
```python
MetadataFactory.create(ds) -> MammographyMetadata
```
Invoca todos los extractores y devuelve un `MammographyMetadata` completo.

#### Desde array numpy (valores por defecto)
```python
MetadataFactory.create_default(pixel_array=None, defaults=None) -> MammographyMetadata
```
Crea metadata con campos derivados del array (`rows`, `columns`, `bits_stored`,
windowing estimado) y rellena el resto con `None`.
Si se pasa `defaults`, se mezcla sobre la base calculada.

```python
MetadataFactory.create_default_from_array(pixel_array) -> MammographyMetadata
```
Alias de `create_default(pixel_array=pixel_array)`.

#### Desde diccionario
```python
MetadataFactory.create_from_dict(defaults, pixel_array=None) -> MammographyMetadata
```
Mezcla el diccionario sobre los valores por defecto del array.
Solo es necesario incluir los campos que quieras sobreescribir.

```python
MetadataFactory.create_from_dict(
    {"vendor": {"manufacturer": "ACME", "model_name": "X"}},
    pixel_array=arr,
)
```

#### Desde archivo JSON
```python
MetadataFactory.create_from_file(file_path, pixel_array=None, preset_name=None) -> MammographyMetadata
```
- Si el JSON contiene directamente secciones (`patient`, `vendor`, etc.): se trata como defaults planos.
- Si el JSON contiene una colección de presets, es obligatorio pasar `preset_name`.

```python
# Archivo de defaults planos
MetadataFactory.create_from_file("mis_defaults.json", pixel_array=arr)

# Archivo de colección de presets
MetadataFactory.create_from_file("presets.json", pixel_array=arr, preset_name="Hologic")
```

#### Desde preset por nombre
```python
MetadataFactory.create_preset(
    name,
    pixel_array=None,
    presets=None,        # dict en memoria; si None, carga presets.json
    presets_path=None,   # ruta alternativa al JSON de presets
    overrides=None,      # dict con valores a aplicar encima del preset
) -> MammographyMetadata
```

```python
MetadataFactory.create_preset("Hologic", pixel_array=arr)
MetadataFactory.create_preset(
    "GE",
    pixel_array=arr,
    overrides={"breast": {"laterality": "R", "view": "CC"}},
)
```

### Refresco de metadata tras transformaciones

```python
MetadataFactory.refresh_image_metadata(
    metadata,
    pixel_array,
    image_overrides=None,
) -> MammographyMetadata
```
Recalcula los campos derivados del array actual (`rows`, `columns`, `bits_stored`,
`window_center`, `window_width`) y los sobreescribe en la metadata existente,
preservando `vendor`, `patient`, `breast` y `acquisition` sin cambios.
Se puede pasar `image_overrides` para actualizar también campos concretos de `ImageInfo`
(por ejemplo, `window_center_width_explanation` o `photometric_interpretation`).

> Este método es llamado automáticamente por `MammographyDicom` tras cada transformación
> de imagen (`initialize_image`, `normalize`).

### Utilidades

```python
MetadataFactory.to_dict(metadata) -> dict
```
Convierte `MammographyMetadata` a diccionario anidado (vía `dataclasses.asdict`).
Útil para serialización o para inspeccionar el estado.

---

## `presets.json`

Colección de valores predefinidos por fabricante.
Se carga automáticamente cuando se llama a `create_preset` sin `presets_path`.

**Estructura de cada preset** (solo los campos que difieren del default):

```json
"NombrePreset": {
  "vendor": {
    "manufacturer": "...",
    "model_name": "..."
  },
  "image": {
    "photometric_interpretation": "MONOCHROME2",
    "presentation_lut_shape": "IDENTITY",
    "voi_lut_function": "LINEAR"
  }
}
```

**Presets disponibles:**

| Preset | Fabricante | Modelo | VOI LUT |
|---|---|---|---|
| `Hologic` | HOLOGIC, Inc. | Selenia Dimensions | LINEAR |
| `GE` | GE Healthcare | Senographe Pristina | SIGMOID |
| `Siemens` | Siemens | — | LINEAR |

Para añadir un nuevo preset, edita `presets.json` siguiendo la estructura anterior.
Los campos no incluidos heredan los valores por defecto del array.

---

## `build.py`

Interfaz simplificada para construir metadata directamente desde un `pydicom.Dataset`.

```python
from api_stable.metadata.build import build_metadata

ds = pydicom.dcmread("archivo.dcm")
metadata = build_metadata(ds)
```

Equivalente a `MetadataFactory.create(ds)`.

---

## Lógica de merge

Todos los constructores basados en defaults siguen este orden de precedencia
(de menor a mayor prioridad):

```
base vacía (Nones)
    ↓
valores derivados del array (rows, columns, bits_stored, windowing)
    ↓
preset o defaults del fabricante
    ↓
overrides explícitos
```

El merge es profundo: solo sobreescribe los campos mencionados, sin borrar el resto.
