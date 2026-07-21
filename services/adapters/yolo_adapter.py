from results_api.metadata.metadata import Detection, DetectionResult

class YoloAdapter:
    @staticmethod
    def to_detection_result(yolo_output):
        detections = []
        for box, score, cls in ...:
            detections.append(
                Detection(
                    label=cls,
                    confidence=score,
                    x_min=box[0],
                    y_min=box[1],
                    x_max=box[2],
                    y_max=box[3],
                )
            )

        return DetectionResult(
            model_name="YOLO",
            model_version="1.0.0",
            detections=detections,
        )