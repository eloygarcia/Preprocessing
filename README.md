# Preprocessing

Pequena libreria para preprocesado de imagenes de mamografia (DICOM y raster), con utilidades para:

- Resumen y exportacion de metadatos.
- Exportacion de tags DICOM a CSV.
- Carga y normalizacion de imagenes.
- Segmentacion de region mamaria.
- Construccion de mascaras etiquetadas (mama y pectoral).
- Flujo especifico para CSAWS.

## Indice del proyecto

### Estructura

```text
Preprocessing/
├── extract_dicoms.py
├── export_dicom_pngs.py
├── requirement.txt
├── notebooks/
│   ├── 00_inbreast_visualization.ipynb
│   ├── 01_csaws_visualization.ipynb
│   ├── 02_cmmd_breast_regions.ipynb
│   └── 03_inbreast_breast_regions.ipynb
└── src/
    ├── __init__.py
    ├── csaws.py
    ├── image_summary.py
    ├── preprocessing.py
    └── visualization.py
```

### Modulos

- `src/preprocessing.py`
  - Lectura de metadatos DICOM.
  - Exportacion de datasets de metadatos y de tags DICOM.
  - Carga de pixeles DICOM, windowing, segmentacion y aplicacion de mascara.
  - Generacion y guardado de mascaras etiquetadas para INBreast.

- `src/visualization.py`
  - Listado/carga de imagenes DICOM.
  - Visualizacion rapida con Matplotlib.

- `src/image_summary.py`
  - Listado de imagenes raster (PNG, JPG, TIF, ...).
  - Extraccion y exportacion de resumen de imagenes raster a CSV.

- `src/csaws.py`
  - Utilidades para dataset CSAWS.
  - Carga de imagen base y labels (`mammary_gland`, `pectoral_muscle`).
  - Creacion de mascara combinada y exportacion de resumen a CSV.

- `extract_dicoms.py`
  - CLI para descubrimiento recursivo de DICOMs y exportacion masiva de tags a CSV.

- `export_dicom_pngs.py`
  - CLI para convertir un dataset DICOM a PNG de 8 bits.
  - Mantiene la estructura relativa de carpetas bajo una nueva carpeta raiz.

- `src/__init__.py`
  - Re-exporta la API publica principal para usar el paquete desde un unico punto de entrada.

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
from src import (
    list_dicom_images,
    load_dicom_pixels,
    apply_windowing,
    segment_breast_region,
    save_labeled_mask,
)

dicoms = list_dicom_images()
image = load_dicom_pixels(dicoms[0])
windowed = apply_windowing(image)
mask = segment_breast_region(windowed)
output_path = save_labeled_mask(dicoms[0])

print(output_path)
```

### 2) Exportar metadatos DICOM

```python
from src import list_dicom_images, export_metadata_dataset

dicoms = list_dicom_images()
csv_path = export_metadata_dataset(dicoms, output_path="./data/inbreast_metadata.csv")
print(csv_path)
```

### 3) Exportar tags DICOM con CLI

```bash
python extract_dicoms.py /ruta/al/dataset /ruta/salida/tags.csv \
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
from src import (
    list_csaws_images,
    create_csaws_combined_mask,
    save_csaws_dataset_combined_masks,
)

images = list_csaws_images()
mask = create_csaws_combined_mask(images[0])
saved = save_csaws_dataset_combined_masks(images[:10], output_dir="./data/csaws_masks")

print(mask.shape, len(saved))
```

### 5) Convertir un dataset DICOM a PNG de 8 bits

```bash
python export_dicom_pngs.py /ruta/dataset_dicom /ruta/dataset_png \
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

## Notebooks

- `notebooks/00_inbreast_visualization.ipynb`: exploracion visual de INBreast.
- `notebooks/01_csaws_visualization.ipynb`: exploracion visual de CSAWS.
- `notebooks/02_cmmd_breast_regions.ipynb`: visualizacion de bounding boxes de regiones mamarias en CMMD.
- `notebooks/03_inbreast_breast_regions.ipynb`: visualizacion de bounding boxes de regiones mamarias en INBreast.

## Notas

- Muchas rutas por defecto apuntan a directorios locales concretos del autor (por ejemplo en `~/Escritorio/Datasets/...`).
- Para reproducibilidad en otros entornos, pasa `dataset_dir`, `output_path`, `masks_dir` y `output_dir` de forma explicita en tus scripts.
