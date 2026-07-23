import json
import importlib
from pathlib import Path

import requests


class PluginManager:
    def __init__(self, plugins):
        self.plugins = plugins
        self.catalog = {}

    def discover(self):
        for plugin in self.plugins:
            try:
                metadata = requests.get(
                    f"{plugin}/metadata"
                ).json()

                self.catalog[
                    metadata["name"]
                ] = {
                    "url": plugin,
                    "metadata": metadata,
                    "status": "online"
                }
            except Exception as e:
                print(
                    f"Error descubriendo {plugin}: {e}"
                )

    def refresh_status(self):
        for name, plugin in self.catalog.items():
            try:
                health = requests.get(
                    f"{plugin['url']}/health"
                ).json()
                plugin["status"] = health["status"]
            except Exception:
                plugin["status"] = "offline"

    def get_catalog(self):
        return self.catalog
    
    def get_algorithm(self, name):
        return self.catalog[name]