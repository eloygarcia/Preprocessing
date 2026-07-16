# processing

Funciones puras de procesado de imagen para mamografía.
**Sin dependencias de DICOM ni de metadata**: reciben y devuelven arrays numpy y parámetros numéricos.

## Archivos

| Archivo | Contenido |
|---|---|
| `photometric.py` | `normalize_image`, `calculate_windowing`, `apply_windowing` |
| `apply_windowing.py` | Implementaciones internas `_apply_windowing_np_v1` / `_apply_windowing_np_v2` |

---

## `photometric.py`

### `normalize_image`

```python
normalize_image(image: np.ndarray) -> np.ndarray
```

Normalización min-max al rango [0, 1].

- Preserva el `dtype` del array de entrada.
- Si el array es constante (min == max), devuelve un array de ceros sin lanzar error.

```python
normalized = normalize_image(pixel_array)
# resultado en [0.0, 1.0]
```

---

### `calculate_windowing`

```python
calculate_windowing(
    image: np.ndarray,
    method: str = 'breast_tissue',
    exclude_background: bool = True,
) -> tuple[int, int]   # (window_center, window_width)
```

Calcula automáticamente parámetros de windowing óptimos a partir del histograma.
Útil cuando los tags DICOM de windowing no están disponibles (datasets anonimizados).

**Métodos disponibles:**

| Método | Descripción | Recomendado para |
|---|---|---|
| `breast_tissue` | Percentiles 25-95 × 1.5 (default) | Mamografía general |
| `percentile_1_99` | Percentiles 1-99 | Uso general robusto |
| `percentile_2_98` | Percentiles 2-98 | Conservador |
| `percentile_5_95` | Percentiles 5-95 | Alto contraste |
| `statistical` | Media ± 2σ | Distribuciones gaussianas |
| `statistical_wide` | Media ± 3σ | Distribuciones con colas |
| `full_range` | Min - Max | Sin recorte |
| `histogram_peak` | FWHM del pico del histograma | Imágenes bimodales |

**Comportamiento con background:**
- `exclude_background=True` (default): ignora píxeles con valor 0 antes de calcular.
- Si todos los píxeles son 0, lanza `ValueError`.

```python
center, width = calculate_windowing(pixel_array, method='breast_tissue')
```

---

### `apply_windowing`

```python
apply_windowing(
    arr: np.ndarray,
    window_center: float,
    window_width: float,
    voi_func: str = 'LINEAR',    # 'LINEAR', 'LINEAR_EXACT', 'SIGMOID'
    y_min: float = 0,
    y_max: float = 255,
    backend: str = 'np_v2',      # 'np_v1', 'np_v2'
) -> np.ndarray
```

Aplica la transformación VOI LUT estándar DICOM (PS3.3 C.11.2).

- El array de salida queda en el rango `[y_min, y_max]`.
- `np_v2` (default) es más rápido que `np_v1` para arrays grandes.
- Backend `torch` está preparado en `apply_windowing.py` pero desactivado.

```python
windowed = apply_windowing(
    pixel_array,
    window_center=1500,
    window_width=3000,
    y_min=0,
    y_max=255,
)
```

**Funciones VOI LUT:**

| `voi_func` | Comportamiento |
|---|---|
| `LINEAR` | Rampa lineal con ajuste ±0.5 (DICOM estándar) |
| `LINEAR_EXACT` | Rampa lineal sin ajuste |
| `SIGMOID` | Curva sigmoide suave, evita clipping duro |

---

## `apply_windowing.py`

Implementaciones internas de bajo nivel. No deben importarse directamente.

| Función | Descripción |
|---|---|
| `_apply_windowing_np_v1` | Implementación con operaciones vectorizadas booleanas (más legible) |
| `_apply_windowing_np_v2` | Implementación con producto matricial optimizado (más rápida) |

Ambas siguen la misma firma:

```python
_apply_windowing_np_v*(arr, window_width, window_center, voi_func, y_min, y_max)
```

---

## Relación con el resto de la API

```
MammographyDicom._apply_windowing()
        │
        │  resuelve parámetros desde metadata.image
        ▼
MammographyImage.apply_windowing(window_center, window_width, voi_lut_function)
        │
        │  llama con parámetros explícitos
        ▼
processing.photometric.apply_windowing(arr, window_center, window_width, ...)
        │
        ▼
processing.apply_windowing._apply_windowing_np_v2(...)
```
