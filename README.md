# Preprocessing

Libreria para preprocesado de imagenes de mamografia (DICOM y PNG), con utilidades para:

- API estable de carga, extraccion de metadatos y preprocesado (`api_stable`).
- Resumen y exportacion de metadatos.
- Exportacion de tags DICOM a CSV.
- Carga y normalizacion de imagenes.
- Segmentacion de region mamaria.
- Construccion de mascaras etiquetadas (mama y pectoral).

## Estructura del proyecto

```text
Preprocessing/
├── api_stable/                  ← API estable de mamografia (ver api_stable/README.md)
│   ├── mammography.py
│   ├── models/
│   ├── extractors/
│   ├── metadata/
│   └── processing/
├── tests/                       ← Suite pytest automática (ver tests/README.md)
│   ├── conftest.py
│   ├── test_processing.py
│   ├── test_models.py
│   ├── test_metadata.py
│   └── test_mammography.py
├── test_api/                    ← Notebooks de prueba interactiva (ver test_api/README.md)
│   ├── 01_api_smoke_test.ipynb
│   ├── 02_image_pipeline_test.ipynb
│   ├── 03_batch_metadata_validation.ipynb
│   └── 05_From_PNG.ipynb
├── image/
│   ├── apply_windowing.py
│   ├── calculate_windowing.py
│   ├── csaws.py
│   ├── image_summary.py
│   ├── preprocessing.py
│   └── visualization.py
├── metadata/
│   └── extract_metadata.py
├── utils/
│   ├── extract_dicoms.py
│   ├── export_dicom_pngs.py
│   ├── utils.py
│   └── yolox_interface.py
├── common_tasks/
│   ├── serve/
│   └── wrappers/
├── notebooks/
│   ├── 00_inbreast_visualization.ipynb
│   ├── 01_csaws_visualization.ipynb
│   ├── 02_cmmd_breast_regions.ipynb
│   ├── 03_mammomx_visualization.ipynb
│   ├── 04_vindr_visualization.ipynb
│   ├── 05_yolox_inference_demo.ipynb
│   └── XX_vendor_device_barplots.ipynb
├── docker/
│   └── Dockerfile.services
├── Dockerfile
└── requirement.txt
```

## api_stable (punto de entrada principal)

API con separación clara por capas para trabajar con mamografías DICOM y PNG.
Consulta [api_stable/README.md](api_stable/README.md) para detalles completos.

```python
from api_stable.mammography import MammographyDicom

# Desde DICOM
mammo = MammographyDicom.from_dicom("archivo.dcm")

# Desde PNG con preset de fabricante
mammo = MammographyDicom.from_png("imagen.png", metadata_preset="Hologic")

# Pipeline completo
mammo.initialize_image().normalize()
print(mammo.metadata)
print(mammo.image.get_history())
```

## Tests automáticos

```bash
python -m pytest tests/ -v
```

89 tests cubriendo las capas `processing`, `models`, `metadata` y `mammography`.
Consulta [tests/README.md](tests/README.md) para el detalle completo.

## Módulos legacy

- `image/preprocessing.py`
  - Lectura de metadatos DICOM.
  - Exportacion de datasets de metadatos y de tags DICOM.
  - Carga de pixeles DICOM, windowing, segmentacion y aplicacion de mascara.
  - Generacion y guardado de mascaras etiquetadas para INBreast.

- `image/visualization.py`
  - Listado/carga de imagenes DICOM.
  - Visualizacion rapida con Matplotlib.

- `image/image_summary.py`
  - Listado de imagenes raster (PNG, JPG, TIF, ...).
  - Extraccion y exportacion de resumen de imagenes raster a CSV.

- `image/csaws.py`
  - Utilidades para dataset CSAWS.
  - Carga de imagen base y labels (`mammary_gland`, `pectoral_muscle`).
  - Creacion de mascara combinada y exportacion de resumen a CSV.

- `utils/extract_dicoms.py`
  - CLI para descubrimiento recursivo de DICOMs y exportacion masiva de tags a CSV.

- `utils/export_dicom_pngs.py`
  - CLI para convertir un dataset DICOM a PNG de 8 bits.
  - Mantiene la estructura relativa de carpetas bajo una nueva carpeta raiz.

- `image/__init__.py`
  - Re-exporta parte de la API publica principal para usar el paquete desde un unico punto de entrada.

## Instalacion

Se recomienda usar entorno virtual.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

## Uso rapido

### 1) Trabajar con DICOM desde Python

```python
from image.visualization import list_dicom_images
from image.apply_windowing import apply_windowing
from image.preprocessing import load_dicom_pixels, segment_breast_region, save_labeled_mask

dicoms = list_dicom_images()
image = load_dicom_pixels(dicoms[0])
windowed = apply_windowing(image)
mask = segment_breast_region(windowed)
output_path = save_labeled_mask(dicoms[0])

print(output_path)
```

### 2) Exportar metadatos DICOM

```python
from image.visualization import list_dicom_images
from image.preprocessing import export_metadata_dataset

dicoms = list_dicom_images()
csv_path = export_metadata_dataset(dicoms, output_path="./data/inbreast_metadata.csv")
print(csv_path)
```

### 3) Exportar tags DICOM con CLI

```bash
python utils/extract_dicoms.py /ruta/al/dataset /ruta/salida/tags.csv \
  --include-extensionless \
  --workers auto \
  --batch-size 500
```

Opciones utiles del CLI:

- `--include-private-tags`: incluye tags privados.
- `--exclude-file-meta`: excluye file meta tags.
- `--exclude-pixel-summary`: elimina columnas de resumen de pixel array.
- `--delimiter ';'`: cambia separador de salida.
- `--extensionless-only`: busca solo DICOM sin extension.

### 4) Flujo CSAWS

```python
from image.csaws import list_csaws_images, create_csaws_combined_mask, save_csaws_dataset_combined_masks

images = list_csaws_images()
mask = create_csaws_combined_mask(images[0])
saved = save_csaws_dataset_combined_masks(images[:10], output_dir="./data/csaws_masks")

print(mask.shape, len(saved))
```

### 5) Convertir un dataset DICOM a PNG de 8 bits

```bash
python utils/export_dicom_pngs.py /ruta/dataset_dicom /ruta/dataset_png \
  --include-extensionless \
  --workers auto
```

Cada DICOM se convierte a un PNG en escala de grises de 8 bits y se guarda en la misma ruta relativa dentro de la nueva raiz. Por ejemplo:

```text
/dataset_origen/case_001/study_a/image_01.dcm
->
/dataset_png/case_001/study_a/image_01.png
```

Opciones utiles:

- `--use-windowing`: aplica windowing antes de convertir a 8 bits.
- `--include-extensionless`: incluye DICOM sin extension.
- `--extensionless-only`: procesa solo DICOM sin extension.
- `--workers auto`: paraleliza la conversion.

### 6) Revisar en batch imagen + segmentacion solapada (terminal)

```bash
python -m image.visualization /ruta/imagenes /ruta/mascaras \
  --batch-size 8 \
  --columns 4 \
  --alpha 0.35
```

Por defecto, para cada imagen busca una mascara en `/ruta/mascaras` con nombre `<stem>.png`.

Opciones utiles:

- `--mask-suffix _mask`: usa `<stem>_mask.png`.
- `--mask-extension .tif`: cambia extension de mascara.
- `--mask-threshold 0`: umbral para binarizar mascara.
- `--start-index 100`: comienza en un indice concreto.
- `--max-images 64`: limita la revision a N imagenes.
- `--non-recursive`: no recorre subcarpetas.

Tambien puedes usar un CSV para mapear rutas exactas imagen-mascara:

```csv
image_path,mask_path
/ruta/imagenes/case_001.dcm,/ruta/mascaras/case_001.png
/ruta/imagenes/case_002.dcm,/ruta/mascaras/case_002.png
```

```bash
python -m image.visualization --pairs-csv /ruta/pairs.csv
```

Opciones de CSV:

- `--csv-image-column image_path`
- `--csv-mask-column mask_path`
- `--csv-delimiter ';'`
- Si usas la misma columna para imagen y mascara (por ejemplo `file_name`),
  la mascara se busca con la extension definida en `--mask-extension` (por defecto `.png`).

Si en el CSV usas rutas relativas, puedes pasar carpetas base:

```bash
python -m image.visualization /base/imagenes /base/mascaras --pairs-csv /ruta/pairs.csv
```

## Notebooks

- `notebooks/00_inbreast_visualization.ipynb`: exploracion visual de INBreast.
- `notebooks/01_csaws_visualization.ipynb`: exploracion visual de CSAWS.
- `notebooks/02_cmmd_breast_regions.ipynb`: visualizacion de bounding boxes de regiones mamarias en CMMD.
- `notebooks/03_mammomx_visualization.ipynb`: exploracion visual de Mammo-MX.
- `notebooks/04_vindr_visualization.ipynb`: exploracion visual de VinDr.
- `notebooks/05_yolox_inference_demo.ipynb`: prueba completa de inferencia con YOLOX y segmentacion MAseg sobre imagenes DICOM.
- `notebooks/XX_vendor_device_barplots.ipynb`: analisis de fabricantes y dispositivos.

## Notas

- Muchas rutas por defecto apuntan a directorios locales concretos del autor (por ejemplo en `~/Escritorio/Datasets/...`).
- Para reproducibilidad en otros entornos, pasa `dataset_dir`, `output_path`, `masks_dir` y `output_dir` de forma explicita en tus scripts.

## Guia de uso

- Consulta `usage.txt` para un flujo completo de trabajo con Docker y notebooks.
- Incluye pasos para integrar `MyYoloX` y ejecutar inferencia desde notebooks con `utils.yolox_interface.YOLOXNotebookInterface`.

## Docker y servicios de inferencia

El proyecto soporta dos formas principales de ejecucion:

- Contenedor unico para trabajo interactivo (scripts y notebooks).
- Stack de servicios con Docker Compose (notebook + APIs de modelos).

### Build de imagen

```bash
docker build -f Dockerfile -t preprocessing:dev .
```

El `Dockerfile` base instala dependencias comunes del proyecto. Los bloques de instalacion opcional de `MyYoloX` y MAseg estan dejados comentados como referencia para un build manual.

### Stack con Docker Compose

Archivo: `docker-compose.yml`
Dockerfile de servicios: `docker/Dockerfile.services`

```bash
docker compose up --build
```

Servicios disponibles:

- Notebook (JupyterLab): `http://localhost:8888`
- YOLOX API: `http://localhost:8001`
- MAseg API: `http://localhost:8002`

Health checks rapidos:

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## Wrappers por tarea

Para estandarizar inferencia de modelos por tarea, los wrappers se ubican en:

- `common_tasks/wrappers/`
- Documentacion de organizacion de tareas: `common_tasks/README.md`

Wrappers actuales:

- Deteccion YOLOX para uso en notebook: `utils/yolox_interface.py`
- Segmentacion MAseg: `common_tasks/wrappers/segmentation/maseg_wrapper.py`

## Notas de rutas

- En este repositorio la raiz de codigo Python vive en `image/`, `metadata/`, `utils/` y `common_tasks/`, no en un paquete `src/`.
- Los comandos CLI de ejemplo asumen que se ejecutan desde la raiz del repositorio.
- Dar a cada servicio su stage/imagen en `docker/Dockerfile.services`.
- Montar codigo y pesos como volumenes (`/workspace`) para iterar rapido.
- Reconstruir solo el servicio afectado cuando cambian dependencias.
