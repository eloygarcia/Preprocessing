# image

Modulo principal de procesamiento y visualizacion de imagenes.

## Contenido

- `preprocessing.py`: lectura DICOM, extraccion de metadatos/tags, segmentacion de mama, exportacion de mascaras y conversion a PNG.
- `visualization.py`: utilidades de visualizacion de DICOM y overlays de imagen+mascara.
- `image_summary.py`: resumen de imagenes raster a CSV.
- `csaws.py`: utilidades especificas del dataset CSAWS y construccion de mascaras combinadas.
- `apply_windowing.py`: implementaciones de windowing (`np_v1`, `np_v2`, `torch`).
- `calculate_windowing.py`: calculo automatico de parametros de windowing y analisis por dataset.

## Nota de mantenimiento

Esta carpeta contiene logica que tambien existe en `Windowing/` (windowing y calculo de parametros). Ver `to_improve.txt` para consolidacion.
