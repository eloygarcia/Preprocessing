# results_api/test

Pruebas de la capa `results_api`.

## Contenido

- `results_test.py`: tests automáticos con `pytest`.
- `Untitled.ipynb`: validación manual/interactiva con ejemplos de uso.

## Ejecutar tests automáticos

```bash
python -m pytest results_api/test/results_test.py -q
```

## Ejecutar notebook manual

1. Abrir `results_api/test/Untitled.ipynb`.
2. Ejecutar celdas en orden.
3. Verificar:
   - creación de predicciones
   - agregación por `StudyResult`
   - serialización a diccionario
