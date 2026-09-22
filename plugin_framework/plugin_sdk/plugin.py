from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Union

import yaml


@dataclass(frozen=True)
class PluginManifest:
    """Runtime manifest describing a plugin contract."""

    name: str
    version: str
    description: str = ""
    entrypoint: str = "app:app"
    port: int = 8000
    gpu: bool = True
    docker_image: str | None = None
    base_image: str | None = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.name or not str(self.name).strip():
            raise ValueError("Plugin name cannot be empty")
        if not self.version or not str(self.version).strip():
            raise ValueError("Plugin version cannot be empty")
        if not self.entrypoint or not str(self.entrypoint).strip():
            raise ValueError("Plugin entrypoint cannot be empty")
        if not isinstance(self.port, int) or self.port <= 0:
            raise ValueError("Plugin port must be a positive integer")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        runtime = data.get("runtime", {}) if isinstance(data.get("runtime"), dict) else {}
        docker = data.get("docker", {}) if isinstance(data.get("docker"), dict) else {}
        name = str(data.get("name") or "").strip()
        version = str(data.get("version") or "").strip()
        description = str(data.get("description") or "")
        entrypoint = str(data.get("entrypoint") or "app:app")
        port = int(runtime.get("port", data.get("port", 8000)))
        gpu = bool(runtime.get("gpu", data.get("gpu", True)))
        docker_image = docker.get("image") or data.get("docker_image")
        base_image = docker.get("base_image") or data.get("base_image")
        tags = data.get("tags", []) or []
        return cls(
            name=name,
            version=version,
            description=description,
            entrypoint=entrypoint,
            port=port,
            gpu=gpu,
            docker_image=docker_image,
            base_image=base_image,
            tags=list(tags),
        )

    @classmethod
    def from_yaml(cls, source: Union[str, Path]) -> "PluginManifest":
        if isinstance(source, Path):
            data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
        else:
            data = yaml.safe_load(source) or {}
        return cls.from_dict(data)

    @classmethod
    def from_json(cls, source: Union[str, Path]) -> "PluginManifest":
        if isinstance(source, Path):
            payload = json.loads(source.read_text(encoding="utf-8"))
        else:
            payload = json.loads(source)
        return cls.from_dict(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "entrypoint": self.entrypoint,
            "port": self.port,
            "gpu": self.gpu,
            "docker_image": self.docker_image,
            "base_image": self.base_image,
            "tags": list(self.tags),
        }


class PluginRuntime:
    """Defines the runtime contract expected from generated plugins."""

    def __init__(self, plugin: "BasePlugin"):
        self.plugin = plugin

    def health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "name": self.plugin.manifest.name,
            "version": self.plugin.manifest.version,
            "gpu": self.plugin.manifest.gpu,
        }

    def metadata(self) -> Dict[str, Any]:
        return self.plugin.manifest.to_dict()


class BasePlugin:
    """Minimal plugin contract that generated plugins should implement."""

    manifest: PluginManifest

    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.runtime = PluginRuntime(self)

    def health(self) -> Dict[str, Any]:
        return self.runtime.health()

    def metadata(self) -> Dict[str, Any]:
        return self.runtime.metadata()

    def predict(self, payload: Any):
        raise NotImplementedError("Plugin predict() must be implemented by subclasses")


class PluginRegistry:
    """Registers and resolves plugin instances by name."""

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> BasePlugin:
        if not isinstance(plugin, BasePlugin):
            raise TypeError("Only BasePlugin instances can be registered")
        self._plugins[plugin.manifest.name] = plugin
        return plugin

    def get(self, name: str) -> BasePlugin:
        return self._plugins[name]

    def list(self) -> Iterable[str]:
        return tuple(self._plugins.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._plugins


class PluginProjectGenerator:
    """Creates a plugin project skeleton with a realistic structure."""

    def generate(self, project_dir: Union[str, Path], name: str, description: str = "") -> PluginManifest:
        folder = Path(project_dir)
        folder.mkdir(parents=True, exist_ok=True)

        manifest = PluginManifest(
            name=name,
            version="0.1.0",
            description=description,
            entrypoint="app:app",
            port=8000,
            gpu=True,
            docker_image=f"preprocessing:{name.lower()}",
            base_image="preprocessing:notebook",
            tags=["mammography"],
        )

        files = {
            "README.md": self._readme(name, description),
            "plugin.yaml": self._plugin_yaml(manifest),
            "plugin.json": self._plugin_json(manifest),
            "api.py": self._api_file(manifest),
            "predictor.py": self._predictor_file(manifest),
            "preprocessing.py": self._preprocessing_file(),
            "postprocessing.py": self._postprocessing_file(),
            "requirements.txt": self._requirements(),
            "Dockerfile": self._dockerfile(manifest),
            "config.yaml": self._config_yaml(),
            "__init__.py": self._init_file(),
        }

        for filename, content in files.items():
            (folder / filename).write_text(content, encoding="utf-8")

        return manifest

    def _readme(self, name: str, description: str) -> str:
        return f"""# {name}

{description or 'Plugin generated with the project SDK.'}

## Purpose

This plugin implements the standard plugin runtime contract and exposes a FastAPI service.

## Endpoints

- `/health`
- `/metadata`
- `/predict`

## Local start

```bash
python api.py
```
"""

    def _plugin_yaml(self, manifest: PluginManifest) -> str:
        return f"""name: {manifest.name}
version: {manifest.version}
description: {manifest.description}

runtime:
  gpu: {str(manifest.gpu).lower()}
  port: {manifest.port}

container:
  image: {manifest.docker_image or 'preprocessing:plugin'}
  base_image: {manifest.base_image or 'preprocessing:notebook'}
"""

    def _plugin_json(self, manifest: PluginManifest) -> str:
        return json.dumps(manifest.to_dict(), indent=2)

    def _api_file(self, manifest: PluginManifest) -> str:
        return f'''from fastapi import FastAPI, Body

from predictor import Predictor

app = FastAPI()
predictor = Predictor()


@app.get("/health")
def health():
    return predictor.health()


@app.get("/metadata")
def metadata():
    return predictor.metadata()


@app.post("/predict")
def predict(request: dict = Body(...)):
    return predictor.predict(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port={manifest.port})
'''

    def _predictor_file(self, manifest: PluginManifest) -> str:
        gpu_literal = "True" if manifest.gpu else "False"
        return f'''from typing import Any

from plugin_framework.plugin_sdk import BasePlugin, PluginManifest


class Predictor(BasePlugin):
    def __init__(self):
        super().__init__(PluginManifest(
            name="{manifest.name}",
            version="{manifest.version}",
            description="{manifest.description}",
            entrypoint="app:app",
            port={manifest.port},
            gpu={gpu_literal},
            docker_image={manifest.docker_image!r},
            base_image={manifest.base_image!r},
        ))

    def predict(self, payload: Any):
        return {{"status": "ok", "payload": payload}}
'''

    def _preprocessing_file(self) -> str:
        return '''def preprocess(payload):
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        return {"items": payload}
    return {"value": payload}
'''

    def _postprocessing_file(self) -> str:
        return '''def postprocess(output):
    return output
'''

    def _requirements(self) -> str:
        return "fastapi\nuvicorn\npydantic\nPyYAML\n"

    def _dockerfile(self, manifest: PluginManifest) -> str:
        return f'''FROM {manifest.base_image or 'preprocessing:notebook'}
WORKDIR /workspace
COPY . /workspace
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE {manifest.port}
CMD ["python", "api.py"]
'''

    def _config_yaml(self) -> str:
        return '''model: default
input_format: numpy
output_format: json
'''

    def _init_file(self) -> str:
        return '"""Generated plugin package."""\n'
