class Pipeline:
    def run(self, study):
        raise NotImplementedError


class MammographyPipeline(Pipeline):
    ALIAS_TO_ALGORITHM = {
        "yolo": "yolox",
        "unet": "unet-segmentation",
        "classification": "resnet-classification",
    }

    def __init__(self, service):
        self.service = service

    @staticmethod
    def _resolve_algorithm(name):
        return MammographyPipeline.ALIAS_TO_ALGORITHM.get(name, name)

    def run(self, study):
        study.roi = self.service.predict(
            self._resolve_algorithm("yolo"),
            study.image,
        )

        study.mask = self.service.predict(
            self._resolve_algorithm("unet"),
            {
                "image": study.image,
                "roi": study.roi,
            },
        )

        study.classification = self.service.predict(
            self._resolve_algorithm("classification"),
            {
                "image": study.image,
                "mask": study.mask,
            },
        )
        return study


PIPELINES = {
    "breast_analysis": [
        "yolo",
        "unet",
        "classification",
    ]
}


class PipelineEngine:
    def __init__(self, service=None):
        self.service = service

    def execute(self, pipeline, study, service=None):
        service = service or self.service
        if service is None:
            raise ValueError("A service instance is required to execute a pipeline")

        if isinstance(pipeline, str):
            steps = PIPELINES.get(pipeline, [])
        else:
            steps = list(pipeline)

        for step in steps:
            algorithm = MammographyPipeline._resolve_algorithm(step)
            if step == "yolo":
                study.roi = service.predict(algorithm, study.image)
            elif step == "unet":
                study.mask = service.predict(algorithm, {"image": study.image, "roi": study.roi})
            elif step == "classification":
                study.classification = service.predict(algorithm, {"image": study.image, "mask": study.mask})
            else:
                study = service.predict(algorithm, study)

        return study