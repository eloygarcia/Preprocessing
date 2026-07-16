# tests

Suite de tests automáticos de `api_stable` usando pytest.

## Estructura

```text
tests/
├── conftest.py            ← fixtures compartidas (arrays numpy, PNGs temporales, archivos JSON)
├── test_processing.py     ← funciones puras de processing
├── test_models.py         ← MammographyImage (capa de modelo de imagen)
├── test_metadata.py       ← MetadataFactory (presets, dict, file, refresh)
└── test_mammography.py    ← MammographyDicom end-to-end
```

## Ejecución

```bash
# Desde la raíz del proyecto
python -m pytest tests/ -v
```

Resultado esperado: **89 tests, 0 fallos**.

## Cobertura por módulo

### `test_processing.py` — 16 tests
Prueba funciones puras de `api_stable/processing/photometric.py`:

| Clase | Qué verifica |
|---|---|
| `TestNormalizeImage` | rango [0,1], imagen constante, shape, dtype |
| `TestEnsureMonochrome2` | inversión MONOCHROME1, no-op para MONOCHROME2 |
| `TestCalculateWindowing` | tipos de retorno, width positivo, imagen todo-ceros, todos los métodos, método inválido |
| `TestApplyWindowing` | clipping entre y_min/y_max, shape, equivalencia np_v1 vs np_v2, backend inválido |

### `test_models.py` — 18 tests
Prueba `api_stable/models/image.py` (`MammographyImage`):

| Clase | Qué verifica |
|---|---|
| `TestMammographyImageConstruction` | shape, dtype, min/max, history vacío, sin dependencia de `ds` |
| `TestMammographyImageCopy` | copia independiente, `to_numpy` |
| `TestNormalize` | historial, retorna `self`, imagen constante sin crash |
| `TestConvertToMonochrome2` | inversión correcta, historial, retorna `self` |
| `TestApplyWindowing` | `last_windowing` poblado, historial, fallback automático, retorna `self` |
| `TestChaining` | encadenamiento completo de 3 operaciones |

### `test_metadata.py` — 22 tests
Prueba `api_stable/metadata/factory.py` (`MetadataFactory`):

| Clase | Qué verifica |
|---|---|
| `TestCreateDefault` | instancia correcta, rows/columns, bits, photometric, windowing calculado, sin array |
| `TestCreateFromDict` | override vendor, override photometric, campos sin mencionar conservan defaults |
| `TestCreatePreset` | Hologic, GE (SIGMOID), Siemens, case-insensitive, preset desconocido, preset custom, overrides sobre preset, rows/columns desde array |
| `TestCreateFromFile` | archivo flat, colección sin nombre lanza error, colección con nombre |
| `TestRefreshImageMetadata` | actualiza rows/cols, conserva vendor, aplica overrides |
| `TestToDict` | retorna dict, roundtrip sin pérdida |

### `test_mammography.py` — 33 tests
Prueba `api_stable/mammography.py` (`MammographyDicom`):

| Clase | Qué verifica |
|---|---|
| `TestFromNumpyArray` | shape, metadata creada, rows/cols, preset, defaults, overrides, metadata explícita |
| `TestFromNumpyPNGPath` | carga desde path PNG, `path` almacenado |
| `TestFromPNG` | carga básica, metadata, preset GE, overrides sobre preset, PNG constante sin crash |
| `TestInitializeImage` | MONOCHROME1→2, MONOCHROME2 sin tocar, windowing en historial, explanation APPLIED, retorna `self` |
| `TestNormalize` | explanation NORMALIZED, historial, retorna `self` |
| `TestMetadataSync` | rows/cols estables, vendor conservado, overrides de breast conservados |
| `TestCopy` | copia independiente, metadata conservada |

## Fixtures disponibles (`conftest.py`)

| Fixture | Tipo | Descripción |
|---|---|---|
| `gray_uint8` | `np.ndarray` | 64×64 uint8, contenido variado |
| `gray_uint16` | `np.ndarray` | 64×64 uint16, rango 12-bit |
| `monochrome1_uint8` | `np.ndarray` | 64×64 uint8 para tests de inversión |
| `constant_uint8` | `np.ndarray` | 32×32 todo ceros, edge cases |
| `png_gray_uint8` | `Path` | PNG temporal escrito desde `gray_uint8` |
| `png_constant` | `Path` | PNG temporal escrito desde `constant_uint8` |
| `presets_path` | `Path` | Ruta al `presets.json` del paquete |
| `custom_presets_file` | `Path` | JSON temporal de un preset de prueba |
| `custom_defaults_file` | `Path` | JSON temporal de defaults planos |

## Añadir nuevos tests

1. Usa las fixtures existentes de `conftest.py` siempre que sea posible.
2. Si necesitas un nuevo fabricante en presets, añádelo primero en `api_stable/metadata/presets.json`
   y añade un test en `TestCreatePreset`.
3. Para tests de DICOM real, añade una fixture en `conftest.py` que apunte a un archivo DICOM
   local conocido.
