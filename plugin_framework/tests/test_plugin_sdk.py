import sys
import types
from pathlib import Path

import numpy as np
import pytest

from plugin_framework.plugin_manager import PluginManager
from plugin_framework.plugin_sdk import (
    BasePlugin,
    PluginManifest,
    PluginProjectGenerator,
    PluginRegistry,
)


def test_manifest_requires_name_and_version():
    with pytest.raises(ValueError):
        PluginManifest(name="", version="0.1.0")

    with pytest.raises(ValueError):
        PluginManifest(name="demo", version="")


def test_manifest_parses_yaml_runtime_metadata():
    yaml_text = """
name: demo
version: 0.2.0
description: Demo plugin
docker:
  image: preprocessing:demo
  base_image: preprocessing:notebook
runtime:
  gpu: true
  port: 8123
"""

    manifest = PluginManifest.from_yaml(yaml_text)
    assert manifest.name == "demo"
    assert manifest.version == "0.2.0"
    assert manifest.port == 8123
    assert manifest.gpu is True
    assert manifest.docker_image == "preprocessing:demo"


def test_registry_registers_plugins():
    class DemoPlugin(BasePlugin):
        def predict(self, payload):
            return {"status": "ok", "payload": payload}

    registry = PluginRegistry()
    plugin = DemoPlugin(PluginManifest(name="demo", version="0.1.0", entrypoint="demo:app"))
    registry.register(plugin)

    assert registry.get("demo") is plugin
    assert "demo" in registry.list()


def test_runtime_contract_returns_metadata_and_health():
    plugin = BasePlugin(PluginManifest(name="demo", version="0.1.0"))

    assert plugin.health()["status"] == "ok"
    assert plugin.metadata()["name"] == "demo"


def test_plugin_manager_discovers_active_docker_plugins(monkeypatch):
    class FakeContainer:
        name = "preprocessing-xai"
        labels = {"ai.plugin": "true", "ai.port": "8004"}

    class FakeDockerClient:
        containers = type("Containers", (), {"list": staticmethod(lambda: [FakeContainer()])})()

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

    fake_docker_module = types.SimpleNamespace(from_env=lambda: FakeDockerClient())
    monkeypatch.setitem(sys.modules, "docker", fake_docker_module)
    monkeypatch.setattr(
        "requests.get",
        lambda url, timeout=1.5: FakeResponse({"name": "xai", "port": 8004, "version": "0.1"}) if "/metadata" in url else FakeResponse({"status": "ok"}),
    )

    manager = PluginManager("/tmp")
    manager.discover()

    assert "xai" in manager.get_catalog()
    assert manager.get_catalog()["xai"].url == "http://preprocessing-xai:8004"


def test_project_generation_creates_expected_files(tmp_path):
    generator = PluginProjectGenerator()
    project_dir = tmp_path / "DemoPlugin"

    manifest = generator.generate(project_dir, "demo", description="Test plugin")

    assert manifest.name == "demo"
    assert (project_dir / "README.md").exists()
    assert (project_dir / "plugin.yaml").exists()
    assert (project_dir / "api.py").exists()
    assert (project_dir / "predictor.py").exists()
    assert (project_dir / "preprocessing.py").exists()
    assert (project_dir / "postprocessing.py").exists()
    assert (project_dir / "Dockerfile").exists()
    assert (project_dir / "config.yaml").exists()

    loaded = PluginManifest.from_yaml(project_dir / "plugin.yaml")
    assert loaded.name == "demo"
    assert loaded.version == "0.1.0"


def test_yolox_plugin_manifest_is_valid():
    manifest_path = Path(__file__).resolve().parents[1] / "plugins" / "YoloPlugin" / "plugin.yaml"

    assert manifest_path.exists(), "YoloPlugin manifest must exist"

    manifest = PluginManifest.from_yaml(manifest_path)

    assert manifest.name == "yolox"
    assert manifest.port == 8006
    assert manifest.gpu is True
    assert manifest.docker_image == "preprocessing:yolox"
    assert manifest.base_image == "preprocessing:notebook"


def test_yolox_results_encoder_keeps_shape_metadata_json_safe():
    from plugin_framework.plugins.YoloPlugin.decoder_service import ResultsEncoder

    encoded = ResultsEncoder.encode({
        "num_detections": 1,
        "image_shape": np.asarray([256, 256, 3]),
    })

    assert encoded["num_detections"] == "1"
    assert encoded["image_shape"] == [256, 256, 3]
