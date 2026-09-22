from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict

from plugin_framework.plugin_sdk import PluginManifest


class Plugin:
    def __init__(self, name: str, url: str, metadata: Dict[str, Any], status: str = "online"):
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


class PluginManager:
    def __init__(self, plugin_root: str | Path | None = None):
        self.plugin_root = Path(plugin_root) if plugin_root is not None else Path(__file__).resolve().parent
        self.catalog: Dict[str, Plugin] = {}

    def discover(self):
        self.catalog = {}

        repo_root = str(Path(__file__).resolve().parents[1])
        work_paths = [p for p in sys.path if Path(p).resolve() != Path(repo_root).resolve()]
        sys.path[:] = work_paths
        try:
            try:
                docker = importlib.import_module("docker")
            except ModuleNotFoundError:
                docker = None
            if docker is not None:
                client = docker.from_env()
                import requests

                for container in client.containers.list():
                    labels = getattr(container, "labels", {}) or {}
                    if labels.get("ai.plugin") == "true":
                        port = labels.get("ai.port") or 8000
                        metadata = {"name": container.name, "port": int(port)}
                        health = {"status": "offline"}
                        resolved_url = None

                        candidates = [
                            f"http://localhost:{port}",
                            f"http://127.0.0.1:{port}",
                            f"http://host.docker.internal:{port}",
                            f"http://{container.name}:{port}",
                        ]

                        for url in candidates:
                            try:
                                metadata_response = requests.get(f"{url}/metadata", timeout=1.5)
                                health_response = requests.get(f"{url}/health", timeout=1.5)
                                if metadata_response.ok:
                                    metadata = metadata_response.json()
                                if health_response.ok:
                                    health = health_response.json()
                                resolved_url = url
                                if metadata.get("name"):
                                    break
                            except Exception:
                                continue

                        if resolved_url is None:
                            resolved_url = f"http://localhost:{port}"

                        plugin = Plugin(
                            name=metadata.get("name", container.name),
                            url=resolved_url,
                            metadata=metadata,
                            status=health.get("status", "offline"),
                        )
                        self.catalog[plugin.name] = plugin
                if self.catalog:
                    return
        finally:
            sys.path.insert(0, repo_root)

        manifests = sorted(self.plugin_root.rglob("plugin.yaml"))
        for manifest_path in manifests:
            try:
                manifest = PluginManifest.from_yaml(manifest_path)
                url = f"http://localhost:{manifest.port}"
                plugin = Plugin(
                    name=manifest.name,
                    url=url,
                    metadata=manifest.to_dict(),
                    status="online",
                )
                self.catalog[plugin.name] = plugin
            except Exception:
                continue

    def refresh_status(self):
        for plugin in self.catalog.values():
            try:
                import requests

                health = requests.get(f"{plugin.get_url()}/health", timeout=1.5).json()
                plugin.set_status(health.get("status", "offline"))
            except Exception:
                plugin.set_status("offline")

    def get_catalog(self):
        return self.catalog

    def get_algorithm(self, name):
        return self.catalog[name]