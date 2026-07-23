import os
from plugin_framework.plugin import Plugin

class BreastSegmentationPlugin(Plugin):
    @property
    def name(self):
        return "Breast Segmentation"

    def execute(self):
        print("Segmentando mama...")