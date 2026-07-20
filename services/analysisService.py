class InferenceService:
    def __init__(self, predictor):
        self.predictor = predictor

    def run(self, image):
        return self.predictor.predict(image)