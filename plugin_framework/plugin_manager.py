import json
import importlib
from pathlib import Path

"""
class PluginManager:
    def __init__(self, plugin_folder="plugins"):
        self.plugin_folder = Path(plugin_folder)
        self.plugins = {}

    def discover(self):
        pass
        
    def load_plugins(self):
        for folder in self.plugin_folder.iterdir():
            if not folder.is_dir():
                continue
            descriptor = folder / "plugin.json"

            if not descriptor.exists():
                continue
            self.load_plugin(folder)


    def load_plugin(self, folder):
        with open(folder / "plugin.json") as f:
            info = json.load(f)

        module_name, class_name = info["entry_point"].split(".")
        module = importlib.import_module(
            f"plugins.{folder.name}.{module_name}"
        )
        #module = importlib.import_module(info["module"])
        #
        #cls = getattr(module, info["class"])

        cls = getattr(module, class_name)
        plugin = cls(info)
        self.plugins[plugin.name] = plugin

    def unload(self):
        pass
    def plugins(self):
        pass
        
    def get(self, name):
        return self.plugins[name]

    def all(self):
        return list(self.plugins.values())
"""

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def register(self, name, predictor):
        #self.plugins[name] = predictor 
        metadata = predictor.get_metadata()
        
        self.plugins[metadata["name"]] = predictor

    def get_algorithm(self, name):
        return self.plugins[name]

    def list_plugins(self):
        return list(self.plugins.keys())

""" CATALOGO DINAMICO """
"""
class PluginManager:

    def __init__(self):
        self.catalog = {}

    def register(self, metadata, url):

        self.catalog[
            metadata["name"]
        ] = {
            "metadata": metadata,
            "url": url,
            "status": "online"
        }
"""

### DESCUBRIMIENTO DE PLUGINS
"""
import requests

class PluginManager:

    def discover(self, endpoints):
        for endpoint in endpoints:
            try:
                metadata = requests.get(
                    f"{endpoint}/metadata",
                    timeout=5
                ).json()

                self.catalog[
                    metadata["name"]
                ] = {
                    "metadata": metadata,
                    "url": endpoint,
                    "status": "online"
                }
            except Exception:
                print(
                    f"ERROR: No se puede conectar con {endpoint}"
                )
"""

## HEALTH MONITOR
"""
def refresh_status(self):
    for name, plugin in self.catalog.items():
        try:
            response = requests.get(
                f"{plugin['url']}/health",
                timeout=2
            )
            plugin["status"] = response.json()[
                "status"
            ]
        except Exception:
            plugin["status"] = "offline"
"""

## MENSAJES DE ERROR
"""
if plugin["status"] != "online":
    raise Exception(
        f"El algoritmo {name} no está disponible"
    )

o :

{
  "success": false,
  "error": "Algorithm yolo is offline"
}

"""