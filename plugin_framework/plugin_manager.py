import json
import importlib
from pathlib import Path

import requests
import docker

## Store plugin information
class Plugin:
    def __init__(
        self,
        name,
        url,
        metadata,
        status="online"
    ):
        self.name = name
        self.url = url
        self.metadata = metadata
        self.status = status
        
    def get_metadata(self):
        return self.metadata

    def get_url(self):
        return self.url

    def is_online(self):
        return self.status == "ok"

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

## Plugins management
class PluginManager:
    def __init__(self,):
        self.catalog = {}

    def discover(self):
        client = docker.from_env()

        for container in client.containers.list():
            if container.labels.get("ai.plugin")=="true":
                port = container.labels.get(
                    "ai.port")
                url = (
                    f"http://{container.name}:{port}"
                )
                print(url)
                try:
                    metadata = requests.get(
                        f"{url}/metadata"
                    ).json()
                    health = requests.get(
                        f"{url}/health"
                    ).json()

                    plugin = Plugin(
                        name = metadata["name"],
                        url = url,
                        metadata = metadata,
                        status = health
                    )
                    self.catalog[plugin.name] = plugin
                except Exception:
                    pass

    def refresh_status(self):
        for name, plugin in self.catalog.items():
            try:
                health = requests.get(
                    f"{plugin.get_url()}/health"
                ).json()
                plugin.set_status( health["status"] )
            except Exception:
                plugin.set_status( "offline" )

    def get_catalog(self):
        return self.catalog
    
    def get_algorithm(self, name):
        return self.catalog[name]