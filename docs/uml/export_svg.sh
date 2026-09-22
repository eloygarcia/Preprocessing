#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UML_DIR="$ROOT_DIR/docs/uml"

if ! command -v dot >/dev/null 2>&1; then
  echo "ERROR: 'dot' (Graphviz) no esta disponible en PATH."
  echo "Sugerencia: conda run -n GeoSpatial bash docs/uml/export_svg.sh"
  exit 1
fi

shopt -s nullglob
dot_files=("$UML_DIR"/*.dot)

if [[ ${#dot_files[@]} -eq 0 ]]; then
  echo "No se encontraron archivos .dot en $UML_DIR"
  exit 0
fi

for dot_file in "${dot_files[@]}"; do
  svg_file="${dot_file%.dot}.svg"
  dot -Tsvg "$dot_file" -o "$svg_file"
  echo "Generado: $svg_file"
done

echo "Exportacion UML completada."