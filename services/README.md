# Services Architecture

Este directorio contiene la capa de aplicacion que orquesta casos de uso sobre `api_stable` y delega inferencia externa en adapters.

## Componentes

- `studyService.py`: carga y validacion de estudios (por ejemplo vistas LCC/RCC/LMLO/RMLO).
- `analysisService.py`: composicion de analisis e invocacion de modelos/servicios.
- `pipelineServices.py`: flujo extremo a extremo para pipelines multi-paso.
- `reportService.py`: generacion de salidas/reportes estructurados.
- `exportService.py`: exportacion de artefactos/resultados.
- `adapters/`: encapsula clientes hacia servicios externos (por ejemplo YOLOX).

## Flujo simplificado

1. Entrada de caso/estudio en un service de aplicacion.
2. Normalizacion y lectura de imagen via `api_stable`.
3. Inferencia mediante adapters cuando aplica.
4. Agregacion de resultados y export/reporte.

## Relacion con otras capas

- Dominio de mamografia: `api_stable/`.
- Wrappers de tareas de inferencia: `common_tasks/wrappers/`.
- Pruebas de servicios: `services/tests/`.

## Notas

- Mantener esta capa sin logica de bajo nivel de pixel; esa responsabilidad vive en `api_stable/processing`.
- Cualquier cambio de contrato en adapters debe reflejarse en tests de `services/tests/`.