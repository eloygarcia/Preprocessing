# Documentacion Viva del Proyecto

Esta carpeta centraliza la documentacion de mantenimiento para que el estado tecnico y funcional del repo se mantenga actualizado.

## Objetivo

- Tener un punto unico para decisiones tecnicas, deuda y arquitectura.
- Evitar que README y notas se desalineen con el codigo real.
- Mantener diagramas de clases/modulos reproducibles.

## Flujo recomendado (cada cambio relevante)

1. Actualizar `to_improve.txt` con cambios de deuda tecnica (que cambia, impacto, prioridad).
2. Actualizar el README del modulo afectado.
3. Si cambian clases o relaciones, regenerar UML en `docs/uml/`.
4. En el commit, agrupar codigo + documentacion del mismo tema.

## Regenerar UML automaticamente

Requisitos:

- `pyreverse` (ya disponible en este entorno).
- Opcional: `graphviz` para exportar a SVG/PNG.

Comandos usados en este repo:

```bash
# Diagrama de clases/paquetes de api_stable
PYTHONPATH=. pyreverse -o dot -p api_stable_classes \
  api_stable.mammography api_stable.study \
  api_stable.models.image api_stable.models.study \
  api_stable.models.metadata api_stable.models

# Diagrama de clases del plugin de explicabilidad
PYTHONPATH=. pyreverse -o dot -p plugin_explainability \
  plugin_framework/plugins/ExplainabilityPlugin/original_src/xai_explainability.py

# Guardar artefactos en docs/uml
mkdir -p docs/uml
mv -f classes_api_stable_classes.dot packages_api_stable_classes.dot docs/uml/
mv -f classes_plugin_explainability.dot docs/uml/
```

Si tienes `dot` (Graphviz), puedes renderizar SVG:

```bash
dot -Tsvg docs/uml/classes_api_stable_classes.dot -o docs/uml/classes_api_stable_classes.svg
dot -Tsvg docs/uml/packages_api_stable_classes.dot -o docs/uml/packages_api_stable_classes.svg
dot -Tsvg docs/uml/classes_plugin_explainability.dot -o docs/uml/classes_plugin_explainability.svg
```

Tambien puedes usar el helper del repo:

```bash
bash docs/uml/export_svg.sh
```

## Convenciones para README

En cada README de modulo, mantener estas secciones minimas:

1. Que hace el modulo.
2. Punto(s) de entrada.
3. Dependencias criticas.
4. Ejemplo rapido de uso.
5. Limitaciones o TODO tecnico.

## Artefactos UML actuales

- `docs/uml/classes_api_stable_classes.dot`
- `docs/uml/packages_api_stable_classes.dot`
- `docs/uml/classes_plugin_explainability.dot`
- `docs/uml/classes_preprocessing.dot` (actualmente casi vacio)
- `docs/uml/packages_preprocessing.dot`
