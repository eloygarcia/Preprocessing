# results_api/metadata

Este módulo define las estructuras de datos base para resultados de algoritmos de mamografía.

## Clases principales

- `Prediction(label, confidence)`
- `Detection(Prediction, bbox)`
- `Classification(Prediction)`
- `Segmentation(Prediction, mask_path)`
- `AlgorithmResult(model_name, model_version, ...)`
- `DetectionResult`, `ClassificationResult`, `SegmentationResult`
- `StudyResult` (agregador)

## Notas de diseño

- `confidence` se valida en `[0, 1]`.
- `Detection.bbox` se valida para evitar coordenadas inválidas.
- Cada `*Result` expone la propiedad uniforme `predictions`.
- `to_dict()` serializa con `dataclasses.asdict`.

## Ejemplo

```python
from results_api.metadata.metadata import Detection, DetectionResult

det = Detection(label="mass", confidence=0.91, bbox=(10, 20, 100, 200))
res = DetectionResult(model_name="YOLO", model_version="1.0", detections=[det])
print(res.predictions)
print(res.to_dict())
```
