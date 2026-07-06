# notebooks

Notebooks para exploracion visual, analisis de datasets y generacion de graficas.

## Notebooks principales

- `00_inbreast_visualization.ipynb`: exploracion visual de INBreast.
- `01_csaws_visualization.ipynb`: exploracion visual de CSAWS.
- `02_cmmd_breast_regions.ipynb`: regiones mamarias en CMMD.
- `05_yolox_inference_demo.ipynb`: demo completo de inferencia YOLOX desde notebook (carga DICOM, preprocesado e inferencia de bounding boxes).
- `04_vendor_device_barplots.ipynb`: analisis de fabricantes/dispositivos y comparativas raw vs corrected.

Nota: para `05_yolox_inference_demo.ipynb`, la imagen Docker del proyecto puede instalar `MyYoloX` automaticamente durante la build (ver `INSTALL_MYYOLOX` en `Dockerfile`).

## Artefactos generados

La carpeta tambien contiene imagenes PNG exportadas desde notebooks (barplots y analisis de gaps), usadas para reportes y documentacion.
