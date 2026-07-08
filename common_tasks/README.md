# common_tasks

Esta carpeta agrupa modelos y utilidades por tipo de tarea de vision.

## Estructura actual

- `breast_location/`: recursos relacionados con localizacion de regiones.
- `segmentation/`: modelos y utilidades de segmentacion.
- `wrappers/`: interfaces estables para ejecutar inferencia desde notebooks o servicios API.
- `serve/`: servicios HTTP (FastAPI) para exponer inferencia de modelos en Docker Compose.

## Convencion de wrappers

La idea es mantener una API consistente por tarea para desacoplar notebooks del detalle interno de cada repo/modelo.

Ejemplos actuales:

- `wrappers/segmentation/maseg_wrapper.py`: wrapper de segmentacion pectoral MAseg.

Siguiente paso recomendado:

- Migrar el wrapper de YOLOX desde `utils/yolox_interface.py` a `common_tasks/wrappers/detection/` manteniendo compatibilidad hacia atras.

## Servicios de inferencia

Servicios disponibles en `serve/`:

- `yolox_api.py`: endpoint de deteccion (`/infer`) y estado (`/health`).
- `maseg_api.py`: endpoint de segmentacion (`/infer`) y estado (`/health`).

Estos servicios se levantan con `docker-compose.yml` en la raiz del proyecto.

## Relacion con notebooks

- `notebooks/05_yolox_inference_demo.ipynb` usa `utils/yolox_interface.py`.
- Los notebooks de exploracion y analisis viven en `notebooks/` en la raiz del proyecto.
