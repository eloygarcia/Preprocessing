# io

Scripts CLI para tareas de entrada/salida sobre datasets DICOM.

## Contenido

- `extract_dicoms.py`: descubrimiento recursivo de DICOM y exportacion de tags/metadatos a CSV.
- `export_dicom_pngs.py`: conversion masiva de DICOM a PNG de 8 bits preservando estructura relativa.
- `__init__.py`: importaciones del paquete (requiere revision, ver `to_improve.txt`).

## Uso rapido

```bash
python utils/extract_dicoms.py /ruta/dataset /ruta/salida.csv --include-extensionless
python utils/export_dicom_pngs.py /ruta/dataset /ruta/salida_png --workers auto
```
