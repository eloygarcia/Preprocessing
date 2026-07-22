import os
from plugin_framework.plugin import Plugin

class ImageClassificationPlugin(Plugin):
    @property
    def name(self):
        return "Breast Segmentation"

    def execute(self):
        print("Segmentando mama...")