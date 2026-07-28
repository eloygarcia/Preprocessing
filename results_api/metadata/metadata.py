from __future__ import annotations
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime
from dataclasses import asdict

## v.2
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    overlays: list
    tables: list
    measurements: list
    metadata: dict

## Base
@dataclass(slots=True)
class ModelInfo:
    name: str
    version: str

@dataclass(slots=True)
class AlgorithmResult:
    model_name: str
    model_version: str
    result_id: str = field(
        default_factory=lambda: str(uuid4())
        )
    created_at: datetime = field(
        default_factory=datetime.now
        )
    execution_time_ms: float | None = None
    preprocessing_version: str | None = None
    docker_image: str | None = None

    @property
    def predictions(self) -> list[Detection | Classification | Segmentation]:
        raise NotImplementedError("Subclasses must expose predictions list")
    
    def to_dict(self):
        return asdict(self)

@dataclass(slots=True)
class Prediction:
    label: str
    confidence: float

    def __post_init__(self):
        if not (0.0 <= float(self.confidence) <= 1.0):
            raise ValueError("confidence must be in [0, 1]")

## Detection results
@dataclass(slots=True)
class Detection(Prediction):
    bbox: tuple[int, int, int, int]

    def __post_init__(self):
        super().__post_init__()
        if len(self.bbox) != 4:
            raise ValueError("bbox must have 4 integers: (x_min, y_min, x_max, y_max)")
        x_min, y_min, x_max, y_max = self.bbox
        if x_min > x_max or y_min > y_max:
            raise ValueError("bbox coordinates are invalid")

@dataclass(slots=True)
class DetectionResult(AlgorithmResult):
    detections: list[Detection] = field(default_factory=list)

    @property
    def predictions(self) -> list[Detection]:
        return self.detections


## Classification results
@dataclass(slots=True)
class Classification(Prediction):
    pass

@dataclass(slots=True)
class ClassificationResult(AlgorithmResult):
    classifications: list[Classification] = field(default_factory=list)

    @property
    def predictions(self) -> list[Classification]:
        return self.classifications

    
## Segmentation results
@dataclass(slots=True)
class Segmentation(Prediction):
    mask_path: str

@dataclass(slots=True)
class SegmentationResult(AlgorithmResult):
    segmentations: list[Segmentation] = field(default_factory=list)

    @property
    def predictions(self) -> list[Segmentation]:
        return self.segmentations


## Study results
@dataclass(slots=True)
class StudyResult:
    results: list[AlgorithmResult] = field(
        default_factory=list
    )

    def add(
        self,
        result: AlgorithmResult
    ) -> None:
        self.results.append(result)

    def get_by_type(
        self,
        result_type: type
    ) -> list:
        return [
            result
            for result in self.results
            if isinstance(result, result_type)
        ]

    @property
    def detections(self):
        return self.get_by_type(
            DetectionResult
        )

    @property
    def classifications(self):
        return self.get_by_type(
            ClassificationResult
        )

    @property
    def segmentations(self):
        return self.get_by_type(
            SegmentationResult
        )

    def to_dict(self):
        return asdict(self)