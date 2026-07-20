# results_api

Estructura de datos para almacenar resultados de algoritmos de:

- detección,
- clasificación,
- segmentación,

y agregarlos por estudio/caso mamográfico.

## Estructura

```text
results_api/
├── metadata/
│   └── metadata.py           # dataclasses de predicciones y resultados
├── test/
│   ├── results_test.py       # tests automáticos (pytest)
│   └── Untitled.ipynb        # test manual / ejemplo interactivo
└── mammographycase.py        # contenedor MammographyCase (imagen + resultados)
```

## Modelo de datos

### Predicciones individuales

- `Prediction(label, confidence)`
- `Detection(Prediction, bbox=(x_min, y_min, x_max, y_max))`
- `Classification(Prediction)`
- `Segmentation(Prediction, mask_path)`

Validaciones incluidas:

- `confidence` debe estar en `[0, 1]`
- `bbox` debe tener 4 valores y coordenadas válidas

### Resultados por algoritmo

- `DetectionResult`
- `ClassificationResult`
- `SegmentationResult`

Todos heredan de `AlgorithmResult`, que incluye metadatos de ejecución:

- `model_name`, `model_version`
- `result_id`, `created_at`
- `execution_time_ms`, `preprocessing_version`, `docker_image`

Cada resultado expone `predictions` como propiedad uniforme.

### Agregación por estudio

`StudyResult` almacena una lista de resultados heterogéneos y permite filtrar por tipo:

- `study_result.detections`
- `study_result.classifications`
- `study_result.segmentations`

## Ejemplo rápido

```python
from results_api.metadata.metadata import (
	StudyResult, Detection, DetectionResult,
	Classification, ClassificationResult,
)

det = Detection(label="mass", confidence=0.94, bbox=(120, 200, 420, 530))
det_result = DetectionResult(model_name="YOLO", model_version="1.0", detections=[det])

cls = Classification(label="malignant", confidence=0.81)
cls_result = ClassificationResult(model_name="ResNet", model_version="2.1", classifications=[cls])

study = StudyResult()
study.add(det_result)
study.add(cls_result)

print(len(study.results))          # 2
print(len(study.detections))       # 1
print(det_result.to_dict())
```

## Tests

Ejecutar tests automáticos:

```bash
python -m pytest results_api/test/results_test.py -q
```

Ejecutar test manual en notebook:

- abrir `results_api/test/Untitled.ipynb`
- ejecutar celdas en orden para crear resultados y verificar serialización