# vendors/RSNA

Herramientas y tablas para armonizar el fabricante/modelo en RSNA.

## Contenido

- `map_rsna_vendor_by_image.py`: script principal para mapear `machine_id` a vendor/model y generar salidas enriquecidas.
- `rsna_machine_vendor_mapping_template.csv`: plantilla de mapeo manual.
- `rsna_vendor_map_full.csv`: salida detallada por imagen.
- `rsna_vendor_map_full_machine_summary.csv`: resumen por maquina.

## Flujo sugerido

1. Completar o revisar la plantilla de mapeo.
2. Ejecutar el script para generar archivos finales.
3. Revisar discrepancias y actualizar el mapping template.
