# test_api

Notebooks de prueba manual e interactiva de la API `api_stable`.

## Notebooks

### 01 - API Smoke Test (`01_api_smoke_test.ipynb`)
Prueba mínima de carga DICOM. Verifica que `MammographyDicom.from_dicom` construye
correctamente el objeto, expone `metadata` e `image`, y que los tipos son correctos.

### 02 - Image Pipeline Test (`02_image_pipeline_test.ipynb`)
Prueba el pipeline de preprocesado:
- `initialize_image()` (MONOCHROME1 → 2 + windowing desde metadata)
- `normalize()`
- Historial de transformaciones (`image.get_history()`)
- Visualización antes/después con Matplotlib.

### 03 - Batch Metadata Validation (`03_batch_metadata_validation.ipynb`)
Recorre un directorio de DICOMs, extrae metadata de cada archivo y construye un
DataFrame resumen con errores separados. Útil para validar compatibilidad con un
nuevo dataset.

### 05 - From PNG with Metadata Presets (`05_From_PNG.ipynb`)
Carga imágenes PNG desde disco e inicializa `MammographyDicom` sin DICOM.
Cubre los tres modos de metadata:

| Modo | Código |
|---|---|
| Preset de fabricante | `from_png(path, metadata_preset="Hologic")` |
| Diccionario | `from_png(path, metadata_defaults={...})` |
| Preset + overrides | `from_png(path, metadata_preset="GE", metadata_overrides={...})` |

Muestra también cómo la metadata de imagen se actualiza automáticamente tras
llamar a `initialize_image()`.

### 06 - Services Integration: YOLOX + BreastSegmentation (`06_services_yolox_breastsegmentation.ipynb`)
Notebook de integración para probar los servicios Docker (`yolox-api` y `maseg-api`)
usando como entrada una imagen preprocesada con `api_stable.MammographyDicom`.

Incluye:
- Carga DICOM con `MammographyDicom.from_dicom`.
- Pipeline `initialize_image().normalize()`.
- Conversión a PNG en memoria para envío por HTTP.
- Health checks e inferencia contra ambos endpoints `/infer`.

## Requisitos

```bash
pip install pydicom numpy pandas matplotlib scikit-image
```

Ejecutar los notebooks desde la raíz del proyecto `Preprocessing`, o dejar que
la celda de configuración de cada notebook ajuste `PROJECT_ROOT` automáticamente.

## Nota sobre rutas

Cada notebook define una variable de ruta (`DICOM_PATH`, `PNG_PATH` o `DATASET_DIR`)
en la celda 3. Actualízala antes de ejecutar si los datos están en un directorio distinto.

