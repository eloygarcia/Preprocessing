# notebooks

Notebooks para exploracion visual, analisis de datasets y generacion de graficas.

## Notebooks principales

- `00_inbreast_visualization.ipynb`: exploracion visual de INBreast.
- `01_csaws_visualization.ipynb`: exploracion visual de CSAWS.
- `02_cmmd_breast_regions.ipynb`: regiones mamarias en CMMD.
- `03_mammomx_visualization.ipynb`: exploracion visual de Mammo-MX.
- `04_vindr_visualization.ipynb`: exploracion visual de VinDr.
- `05_yolox_inference_demo.ipynb`: demo completo de inferencia YOLOX desde notebook (carga DICOM, preprocesado e inferencia de bounding boxes).
- `XX_vendor_device_barplots.ipynb`: analisis de fabricantes/dispositivos y comparativas raw vs corrected.

Nota: para `05_yolox_inference_demo.ipynb`, la imagen Docker de servicios instala `MyYoloX` automaticamente durante la build del target `notebook` (ver `docker/Dockerfile.services`).

Para wrappers reutilizables de tareas (deteccion/segmentacion), se propone usar `common_tasks/wrappers/`.

## Artefactos generados

La carpeta tambien contiene imagenes PNG exportadas desde notebooks (barplots y analisis de gaps), usadas para reportes y documentacion.
