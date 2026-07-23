class AIPlatform:
    def __init__(self):

        self.manager = PluginManager(...)
        self.service = InferenceService(...)
    def predict(
        self,
        algorithm,
        image
    ):
        return self.service.predict(
            algorithm,
            image
        )