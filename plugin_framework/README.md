# Plugin Framework

## Objetivo

La capa de `plugin_framework` define la extensión modular del sistema: cada plugin encapsula un modelo o flujo de inferencia y se expone como un servicio HTTP independiente con un contrato uniforme.

El diseño busca separar tres capas claramente:

- interfaz de runtime del plugin
- metadata declarativa del plugin
- gestión de descubrimiento y catálogo desde el framework

Esto permite integrar modelos de diferentes dominios sin acoplar la lógica de negocio del proyecto principal a cada servicio concreto.

---

## Arquitectura

```text
plugin_framework/
├── README.md
├── aip_platform.py
├── encoder_service.py
├── inference_service.py
├── plugin_manager.py
├── plugin_sdk/
│   ├── README.md
│   ├── __init__.py
│   └── plugin.py
├── plugins/
│   ├── ExplainabilityPlugin/
│   ├── GMICplugin/
│   ├── ImageClassificationPlugin/
│   └── UnetSegmentationPlugin/
├── examples/
│   └── generated_plugin/
└── notebooks temporales / pruebas
```

### Capa de runtime

Cada plugin debe exponer una API HTTP con endpoints mínimos para:

- `/health`: comprobación de estado del servicio
- `/metadata`: metadatos del plugin y manifest
- `/predict`: entrada principal para inferencia

El contrato con FastAPI está definido por la base del SDK y es el mismo para todos los plugins.

### Capa de metadata

La metadata del plugin se declara en `plugin.yaml` y/o `plugin.json`. Este descriptor incluye:

- nombre
- versión
- descripción
- puerto de runtime
- habilitación de GPU
- imagen Docker
- base image
- tags opcionales

El formato base actual es:

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

La clase `PluginManifest` del SDK parsea este YAML y lo convierte en un objeto validado.

### Capa de gestión

`PluginManager` es el componente encargado de:

- localizar plugins dentro de un directorio raíz
- cargar el `plugin.yaml`
- extraer los metadatos de runtime
- construir un catálogo interno con la información del servicio
- consultar health de cada plugin para determinar disponibilidad

---

## Componentes principales

### `plugin_manager.py`

`PluginManager` implementa la gestión del catálogo de servicios.

Flujo funcional actual:

1. buscar recursivamente `plugin.yaml` en el árbol de plugins
2. parsear cada descriptor con `PluginManifest`
3. crear un objeto `Plugin` con `name`, `url`, `metadata`, `status`
4. exponer `catalog` y métodos de acceso
5. consultar `/health` para refrescar estado si el plugin está activo

Pseudo-flujo:

```python
from plugin_framework.plugin_manager import PluginManager

manager = PluginManager("./plugin_framework/plugins")
manager.discover()
print(manager.get_catalog())
```

La intención del diseño es que el catálogo sea un punto central de resolución para componentes superiores, sin acoplar la capa de plataforma a una implementación concreta del modelo.

### `plugin_sdk/plugin.py`

El SDK centraliza la lógica reusable para:

- validar manifiestos
- parsear YAML/JSON
- definir runtime mínimo
- registrar plugins
- generar un proyecto base reproducible

Los elementos clave son:

- `PluginManifest`
- `PluginRuntime`
- `BasePlugin`
- `PluginRegistry`
- `PluginProjectGenerator`

### `aip_platform.py`

Es la capa de coordinación con la plataforma y con los servicios de inferencia. Su responsabilidad principal es orquestar la integración del plugin dentro del sistema principal.

### `inference_service.py`

Se encarga de normalizar la invocación a inferencia y abstraer la lógica del modelo concreto. Su objetivo es que cada plugin comparta la misma entrada/salida del servicio.

### `encoder_service.py`

Se usa para serializar o preparar resultados para el cliente REST y para mantener un esquema consistente entre plugins.

---

## Contrato de plugin

Cada plugin debe seguir esta estructura mínima:

```text
plugin_name/
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
└── __init__.py
```

### Requisitos funcionales

- `plugin.yaml` con metadatos y configuración de runtime
- `api.py` con FastAPI y endpoints HTTP mínimos
- `predictor.py` con la clase `Predictor` o equivalente
- `preprocessing.py` para transformar la entrada antes del modelo
- `postprocessing.py` para transformar la salida del modelo
- `Dockerfile` para despliegue reproducible

---

## Contrato de runtime

La estructura base del plugin responde con este comportamiento mínimo:

### `GET /health`

```json
{"status": "ok", "name": "generated", "version": "0.1.0", "gpu": true}
```

### `GET /metadata`

Devuelve el mismo contenido del manifiesto enriquecido con interpretaciones del runtime, por ejemplo:

```json
{
  "name": "generated",
  "version": "0.1.0",
  "description": "Generated sample plugin",
  "entrypoint": "app:app",
  "port": 8000,
  "gpu": true,
  "docker_image": "preprocessing:generated",
  "base_image": "preprocessing:notebook",
  "tags": ["mammography"]
}
```

### `POST /predict`

Recibe la carga útil del cliente y devuelve el resultado del modelo o del pipeline asociado.

---

## SDK: generación de plugins

El SDK usa `PluginProjectGenerator` para crear un proyecto de plugin con el mínimo viable funcional.

### Ejemplo de uso

```python
from pathlib import Path
from plugin_framework.plugin_sdk import PluginProjectGenerator

project_dir = Path("./generated_plugin")
PluginProjectGenerator().generate(project_dir, "generated", "Generated sample plugin")
```

Esto crea automáticamente:

- `README.md`
- `plugin.yaml`
- `plugin.json`
- `api.py`
- `predictor.py`
- `preprocessing.py`
- `postprocessing.py`
- `requirements.txt`
- `Dockerfile`
- `config.yaml`

### Ejemplo de predictor generado

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

La API generada expone los endpoints mínimos y se levanta con `uvicorn` usando el puerto del manifest.

---

## Plugin lifecycle

El ciclo de vida actual del plugin en este repositorio es el siguiente:

1. definición del manifest (`plugin.yaml`)
2. generación o adaptación del proyecto base
3. implementación del predictor y del pipeline asociado
4. arranque como servicio FastAPI
5. descubrimiento por `PluginManager`
6. registro en catálogo y health checks
7. invocación desde servicios o plataforma

Este modelo da un flujo uniforme para proyectos de clasificación, segmentación, explicabilidad y otros tipos de servicios.

---

## Estado del framework

### Plugins actuales

| Plugin | Propósito | Estado |
|---|---|---|
| `ExplainabilityPlugin` | Explicabilidad de predicciones | Activo / WIP |
| `GMICplugin` | Integración del pipeline GMIC | Experimental |
| `ImageClassificationPlugin` | Clasificación mamográfica | Activo / WIP |
| `UnetSegmentationPlugin` | Segmentación por U-Net | Experimental |

### Deuda técnica actual

- algunos plugins tienen estructura y documentación desalineadas
- hay notebooks temporales y archivos auxiliares mezclados con la lógica real
- varias carpetas necesitan un README específico con estado real y requisitos de ejecución
- `plugin_sdk` aún es una base funcional, pero todavía hay que homologar más casos reales con los plugins existentes

---

## Recomendaciones de consolidación

1. normalizar el formato de `plugin.yaml` entre todos los plugins
2. mantener `plugin.json` y YAML consistentes
3. estandarizar endpoints y nombre de variables por plugin
4. mover notebooks de prueba fuera de la carpeta de plugins
5. documentar cada servicio con su propósito, entrada/salida y requisitos de hardware
6. mantener `PluginManager` como la única puerta de entrada de catálogo del framework

---

## Verificación actual

La base del framework y del SDK ha sido validada con tests reales y con una comprobación de arranque de un plugin generado:

```bash
pytest plugin_framework/tests/test_plugin_sdk.py -q
```

Resultado verificado:

```text
6 passed in 0.03s
```

Además, un plugin generado con el SDK responde correctamente en `/health`:

```json
{"status":"ok","name":"generated","version":"0.1.0","gpu":true}
```

---

## Conclusión

`plugin_framework` ya define una base funcional para servicios modulares con metadatos estandarizados y runtime uniforme. El siguiente paso natural es continuar homogeneizando los plugins reales con el mismo esquema, y usar el SDK como mecanismo central de creación y validación de nuevos servicios.
