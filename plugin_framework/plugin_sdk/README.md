# Plugin SDK

Este kit proporciona la base para definir, validar y generar plugins que siguen el mismo contrato de runtime que usa la capa de servicios del proyecto.

El objetivo es mantener una estructura uniforme para todos los plugins: manifest, salud del servicio, metadatos e interacción con FastAPI.

## Qué incluye

El SDK actual define estos bloques principales:

- `PluginManifest`: validación y parseo de metadatos del plugin.
- `PluginRuntime`: contrato de runtime para `/health` y `/metadata`.
- `BasePlugin`: clase base mínima que todos los plugins deben implementar.
- `PluginRegistry`: registro de plugins por nombre.
- `PluginProjectGenerator`: generador de un esqueleto de plugin completo.

## Contrato de metadata

Los plugins se describen con un archivo `plugin.yaml` o `plugin.json` con metadatos comunes.

Ejemplo de `plugin.yaml`:

```yaml
name: generated
version: 0.1.0
description: Generated sample plugin

runtime:
  gpu: true
  port: 8000

container:
  image: preprocessing:generated
  base_image: preprocessing:notebook
```

La clase `PluginManifest` acepta ese formato y lo normaliza a un objeto Python con validación automática.

### Parseo de ejemplo

```python
from plugin_framework.plugin_sdk import PluginManifest

manifest = PluginManifest.from_yaml("plugin.yaml")
print(manifest.name)
print(manifest.port)
print(manifest.gpu)
```

## Contrato de runtime

Los plugins generados siguen una API mínima con FastAPI:

- `GET /health`: devuelve estado del servicio.
- `GET /metadata`: devuelve los metadatos del manifest.
- `POST /predict`: punto de entrada de inferencia.

La implementación base ya devuelve esta estructura:

```json
{"status": "ok", "name": "generated", "version": "0.1.0", "gpu": true}
```

## Uso básico del SDK

### 1. Generar un plugin

```python
from pathlib import Path
from plugin_framework.plugin_sdk import PluginProjectGenerator

project_dir = Path("./my_plugin")
PluginProjectGenerator().generate(project_dir, "my_plugin", "Mi plugin de ejemplo")
```

Esto crea un conjunto de archivos con la estructura mínima:

```text
my_plugin/
├── README.md
├── plugin.yaml
├── plugin.json
├── api.py
├── predictor.py
├── preprocessing.py
├── postprocessing.py
├── requirements.txt
├── Dockerfile
├── config.yaml
├── __init__.py
```

### 2. Arrancar el servicio generado

```bash
cd my_plugin
python api.py
```

La API creada usa FastAPI y se levanta con el puerto indicado en `plugin.yaml`.

## Ejemplo de plugin generado

El SDK produce un `predictor.py` similar a este:

```python
from typing import Any

from plugin_framework.plugin_sdk import BasePlugin, PluginManifest


class Predictor(BasePlugin):
    def __init__(self):
        super().__init__(PluginManifest(
            name="generated",
            version="0.1.0",
            description="Generated sample plugin",
            entrypoint="app:app",
            port=8000,
            gpu=True,
            docker_image="preprocessing:generated",
            base_image="preprocessing:notebook",
        ))

    def predict(self, payload: Any):
        return {"status": "ok", "payload": payload}
```

Y el `api.py` generado expone:

```python
from fastapi import FastAPI, Body

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Integración con el PluginManager

El `PluginManager` de la capa de framework puede descubrir plugins buscando `plugin.yaml` dentro de un directorio raíz y leer el manifest para construir el catálogo del sistema.

### Ejemplo con plugins reales del repositorio

```python
from pathlib import Path
from plugin_framework.plugin_manager import PluginManager

plugin_root = Path("plugin_framework/plugins").resolve()
manager = PluginManager(plugin_root)
manager.discover()

for name, plugin in manager.get_catalog().items():
    print(name, plugin.metadata)
```

En este repositorio la detección real se ha probado sobre carpetas como:

- `plugin_framework/plugins/ExplainabilityPlugin/`
- `plugin_framework/plugins/ImageClassificationPlugin/`
- `plugin_framework/plugins/UnetSegmentationPlugin/`

y el catálogo generado se compone de los manifests que contienen un `plugin.yaml` válido.

## Validación actual

La base del SDK ha sido validada con tests reales y con un arranque comprobado de un plugin generado:

- `pytest plugin_framework/tests/test_plugin_sdk.py -q` -> `6 passed`
- el plugin generado responde en `/health` con un JSON válido

## Recomendación de uso

Se recomienda usar este SDK como base mínima para cada plugin nuevo, y después personalizar:

- el preprocessing
- el postprocessing
- el predictor
- la carga del modelo
- la lógica del endpoint `/predict`

Esto mantiene la arquitectura consistente con el resto de plugins y facilita la integración con el gestor global del sistema.
