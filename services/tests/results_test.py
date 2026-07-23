from datetime import datetime

import pytest

from services.metadata.metadata import (
    StudyResult,
    Detection,
    DetectionResult,
    Classification,
    ClassificationResult,
    Segmentation,
    SegmentationResult,
)


def test_detection_creation_and_bbox():
    detection = Detection(
        label="mass",
        confidence=0.95,
        bbox=(100, 200, 300, 400),
    )

    assert detection.label == "mass"
    assert detection.confidence == 0.95
    assert detection.bbox == (100, 200, 300, 400)


def test_invalid_confidence_raises():
    with pytest.raises(ValueError):
        Detection(label="mass", confidence=1.5, bbox=(0, 0, 10, 10))


def test_invalid_bbox_raises():
    with pytest.raises(ValueError):
        Detection(label="mass", confidence=0.9, bbox=(50, 10, 20, 40))


def test_detection_result_predictions_property():
    detection = Detection(label="mass", confidence=0.95, bbox=(10, 20, 30, 40))
    result = DetectionResult(
        model_name="YOLO",
        model_version="1.0.0",
        created_at=datetime.now(),
        detections=[detection],
    )

    assert len(result.detections) == 1
    assert result.predictions == result.detections
    assert result.predictions[0].label == "mass"


def test_classification_and_segmentation_results():
    cls = Classification(label="malignant", confidence=0.81)
    seg = Segmentation(label="breast", confidence=0.99, mask_path="mask.png")

    cls_result = ClassificationResult(
        model_name="ResNet",
        model_version="2.1",
        classifications=[cls],
    )
    seg_result = SegmentationResult(
        model_name="UNet",
        model_version="3.0",
        segmentations=[seg],
    )

    assert cls_result.predictions[0].label == "malignant"
    assert seg_result.predictions[0].mask_path == "mask.png"


def test_study_result_grouping_by_type():
    study_result = StudyResult()
    det_result = DetectionResult(
        model_name="YOLO",
        model_version="1.0.0",
        detections=[Detection(label="mass", confidence=0.95, bbox=(0, 0, 10, 10))],
    )
    cls_result = ClassificationResult(
        model_name="ResNet",
        model_version="2.1",
        classifications=[Classification(label="benign", confidence=0.76)],
    )
    seg_result = SegmentationResult(
        model_name="UNet",
        model_version="3.0",
        segmentations=[Segmentation(label="region", confidence=0.92, mask_path="rle.txt")],
    )

    study_result.add(det_result)
    study_result.add(cls_result)
    study_result.add(seg_result)

    assert len(study_result.results) == 3
    assert len(study_result.detections) == 1
    assert len(study_result.classifications) == 1
    assert len(study_result.segmentations) == 1


def test_to_dict_serialization():
    result = DetectionResult(
        model_name="YOLO",
        model_version="1.0.0",
        detections=[Detection(label="mass", confidence=0.95, bbox=(0, 0, 10, 10))],
    )
    result_dict = result.to_dict()

    assert result_dict["model_name"] == "YOLO"
    assert len(result_dict["detections"]) == 1
    assert result_dict["detections"][0]["bbox"] == (0, 0, 10, 10)