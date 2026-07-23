class Pipeline:
    def run(self, study):
        raise NotImplementedError


class MammographyPipeline(Pipeline):
    def __init__(self, service):
        self.service = service
        
    def run(self, study):
        study.roi = self.service.predict(
            "yolo",
            study.image
        )
        
        study.mask = self.service.predict(
            "unet",
            {
                "image": study.image,
                "roi": study.roi
            }
        )
        
        study.classification = self.service.predict(
            "classification",
            {
                "image": study.image,
                "mask": study.mask
            }
        )
        return study

## Metodos declarativos:

PIPELINES = {
    "breast_analysis": [
        "yolo",
        "unet",
        "classification"
    ]
}

class PipelineEngine:
    def execute(
        self,
        pipeline,
        study
    ):
        pass