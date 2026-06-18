# Windowing Module

Módulo completo para calcular y aplicar windowing (ventana de visualización) en imágenes de mamografía.

## 📁 Archivos

### 1. `windowing.py` - Aplicar Windowing
**Propósito:** Aplicar transformación de windowing cuando **ya tienes** los parámetros (Window Center y Width).

**Funciones principales:**
- `apply_windowing()` - Aplica windowing con backend numpy o torch
- `_apply_windowing_np_v1()` - Implementación NumPy (versión pydicom original)
- `_apply_windowing_np_v2()` - Implementación NumPy optimizada
- `_apply_windowing_torch()` - Implementación PyTorch

**Uso:**
```python
from windowing import apply_windowing

# Aplicar windowing conocido
windowed = apply_windowing(
    image,
    window_center=1500,
    window_width=3000,
    voi_func='LINEAR',  # o 'SIGMOID'
    y_min=0,
    y_max=255,
    backend='np_v2'  # 'np_v1', 'np_v2', o 'torch'
)
```

---

### 2. `calculate_windowing.py` - Calcular Parámetros ⭐ NUEVO
**Propósito:** Calcular automáticamente Window Center y Width desde histogramas cuando los metadatos DICOM fueron eliminados.

**Funciones principales:**

#### `calculate_windowing(image, method='percentile_2_98')`
Calcula windowing óptimo para una imagen usando diferentes métodos estadísticos.

**Métodos disponibles:**
- `'percentile_1_99'` - Percentiles 1-99 (robusto, uso general)
- `'percentile_2_98'` - Percentiles 2-98 (más conservador) ⭐ Recomendado
- `'percentile_5_95'` - Percentiles 5-95 (alto contraste)
- `'breast_tissue'` - Optimizado para tejido mamario (25-95 percentil) ⭐⭐ Mejor para mamografía
- `'statistical'` - Media ± 2 desviaciones estándar
- `'statistical_wide'` - Media ± 3 desviaciones estándar
- `'full_range'` - Rango completo (min-max)
- `'histogram_peak'` - Basado en pico del histograma y FWHM

**Ejemplo:**
```python
from calculate_windowing import calculate_windowing
import pydicom

# Cargar imagen
dcm = pydicom.dcmread('mammogram.dcm')
image = dcm.pixel_array

# Calcular windowing (método optimizado para mamografía)
center, width = calculate_windowing(image, method='breast_tissue')
print(f"Window Center: {center}, Window Width: {width}")
```

#### `analyze_dataset_windowing(image_paths, method, num_samples=None)`
Analiza múltiples imágenes para obtener parámetros promedio (más robusto).

**Ejemplo:**
```python
from calculate_windowing import analyze_dataset_windowing
from pathlib import Path

# Obtener archivos DICOM
dicom_files = list(Path("dataset/").glob("*.dcm"))

# Analizar 50 imágenes
stats = analyze_dataset_windowing(
    dicom_files,
    method='breast_tissue',
    num_samples=50
)

print(f"Recommended Center: {stats['recommended_center']}")
print(f"Recommended Width: {stats['recommended_width']}")
```

#### `compare_methods_on_dataset(image_paths, num_samples=50)`
Compara todos los métodos en el dataset para encontrar el mejor.

#### `calculate_all_methods(image)`
Calcula windowing con todos los métodos para una imagen (útil para comparar).

**Presets para Mamografía:**
```python
from calculate_windowing import get_mammography_preset

# Obtener método recomendado
method = get_mammography_preset('breast_optimized')  # Devuelve 'breast_tissue'

# Otros presets disponibles:
# 'standard' -> 'percentile_2_98'
# 'high_contrast' -> 'percentile_5_95'  
# 'wide_latitude' -> 'percentile_1_99'
# 'breast_optimized' -> 'breast_tissue' ⭐
```

---

### 3. `example_windowing.py` - Ejemplos Completos
**Propósito:** Ejemplos prácticos de uso completo.

**Ejemplos incluidos:**
1. **Imagen individual** - Calcular y comparar todos los métodos
2. **Análisis de dataset** - Estadísticas de 50 imágenes
3. **Comparación de métodos** - Ver cuál funciona mejor
4. **Aplicar windowing** - Pipeline completo calcular → aplicar

**Ejecutar:**
```bash
cd Windowing
python example_windowing.py
```

**Genera:**
- `windowing_comparison.png` - Comparación visual de métodos
- `windowing_before_after.png` - Antes/después con histograma
- `inbreast_windowing_statistics.json` - Estadísticas del dataset
- `inbreast_method_comparison.json` - Comparación de todos los métodos

---

## 🎯 Casos de Uso

### Caso 1: Dataset con DICOM completo (tiene Window Center/Width)
```python
import pydicom
from windowing import apply_windowing

dcm = pydicom.dcmread('mammogram.dcm')
image = dcm.pixel_array

# Usar valores del DICOM
center = dcm.WindowCenter
width = dcm.WindowWidth

# Aplicar
windowed = apply_windowing(image, center, width)
```

### Caso 2: Dataset anonimizado sin metadatos (InBreast) ⭐
```python
import pydicom
from calculate_windowing import calculate_windowing, get_mammography_preset
from windowing import apply_windowing

# Cargar imagen
dcm = pydicom.dcmread('inbreast_image.dcm')
image = dcm.pixel_array

# PASO 1: Calcular windowing (porque no está en DICOM)
method = get_mammography_preset('breast_optimized')
center, width = calculate_windowing(image, method=method)

# PASO 2: Aplicar windowing
windowed = apply_windowing(image, center, width)
```

### Caso 3: Usar valores promedio de todo el dataset (más robusto)
```python
from pathlib import Path
from calculate_windowing import analyze_dataset_windowing, save_windowing_report
from windowing import apply_windowing
import pydicom

# PASO 1: Analizar dataset una vez (hacer offline)
dicom_files = list(Path("dataset/").glob("*.dcm"))
stats = analyze_dataset_windowing(dicom_files, method='breast_tissue', num_samples=50)

# Guardar para reutilizar
save_windowing_report(stats, "dataset_windowing.json")

# PASO 2: Usar valores recomendados en todas las imágenes
RECOMMENDED_CENTER = stats['recommended_center']  # e.g., 1450
RECOMMENDED_WIDTH = stats['recommended_width']    # e.g., 2800

# PASO 3: Procesar imágenes
for dcm_path in dicom_files:
    dcm = pydicom.dcmread(dcm_path)
    image = dcm.pixel_array
    windowed = apply_windowing(image, RECOMMENDED_CENTER, RECOMMENDED_WIDTH)
    # ... guardar o procesar
```

---

## 📊 Comparación de Métodos (InBreast)

Resultados esperados al ejecutar `example_windowing.py` en InBreast:

| Método | Window Center | Window Width | Uso Recomendado |
|--------|---------------|--------------|-----------------|
| **breast_tissue** | ~1450 | ~2800 | ⭐⭐ Mejor para mamografía |
| **percentile_2_98** | ~1400 | ~2700 | ⭐ Robusto, general |
| **percentile_1_99** | ~1380 | ~2900 | Amplia latitud |
| **percentile_5_95** | ~1500 | ~2200 | Alto contraste |
| **statistical** | ~1420 | ~2400 | Si distribución normal |
| **histogram_peak** | ~1350 | ~2500 | Basado en moda |
| **full_range** | ~1485 | ~2970 | Rango completo |

*Nota: Valores aproximados, varían por imagen*

---

## 🔧 Instalación de Dependencias

```bash
pip install numpy pydicom matplotlib
# Opcional para backend torch:
pip install torch
```

---

## 📚 Documentación Técnica

### ¿Por qué necesitamos calcular windowing?

**Problema:**  
Los datasets médicos públicos (como InBreast) suelen **eliminar metadatos DICOM** durante la anonimización para proteger privacidad. Esto incluye:
- Window Center (0028,1050)
- Window Width (0028,1051)
- Manufacturer
- Device Serial Number
- etc.

**Sin estos valores**, las imágenes se ven incorrectamente (muy oscuras o muy claras) porque el rango de valores de píxeles (0-4000 para 14-bit) no se mapea correctamente al rango de visualización (0-255).

**Solución:**  
Calcular automáticamente estos parámetros desde la distribución estadística de los píxeles (histograma).

### Métodos Estadísticos Explicados

#### Percentiles (Recomendado)
```
Percentil 2-98 significa:
- 2% de píxeles más oscuros quedan en negro
- 2% de píxeles más claros quedan en blanco
- 96% del rango se distribuye linealmente

Window Center = (p2 + p98) / 2
Window Width = p98 - p2
```

**Ventaja:** Robusto contra outliers (píxeles muy brillantes/oscuros anómalos).

#### Breast Tissue (Mejor para mamografía)
```
Percentil 25-95 con expansión:
- Enfoca el tejido glandular (más denso)
- Incluye grasa (menos densa) con margen
- Expande rango 1.5x para mejor visualización

Window Center = (p25 + p95) / 2
Window Width = (p95 - p25) × 1.5
```

**Ventaja:** Optimizado para la distribución específica de densidades mamarias.

#### Estadístico
```
Media ± desviaciones estándar:
Window Center = mean
Window Width = 4 × std  (±2σ incluye ~95% de valores)
```

**Ventaja:** Simple, funciona si distribución es aproximadamente normal.  
**Desventaja:** Sensible a outliers.

### VOI LUT Functions

#### LINEAR (más común)
```python
# Mapeo lineal del rango [center - width/2, center + width/2] a [0, 255]
if pixel < center - width/2:
    output = 0
elif pixel > center + width/2:
    output = 255
else:
    output = ((pixel - center) / width + 0.5) × 255
```

#### SIGMOID (curva S)
```python
# Transición suave en los extremos
output = 255 / (1 + exp(-4 × (pixel - center) / width))
```

---

## 🎓 Para InBreast Específicamente

**Contexto:**  
InBreast DICOM files fueron **re-generados con MATLAB** y perdieron todos los metadatos del equipo Siemens MammoNovation original.

**Especificaciones conocidas (del paper):**
- Pixel size: 70 μm
- Bit depth original: 14-bit (almacenado como 16-bit en DICOM)
- Rango de valores: ~0-2970 (no todo el rango 16-bit)

**Método recomendado:**
```python
method = 'breast_tissue'  # Optimizado para mamografía
center, width = calculate_windowing(image, method='breast_tissue')
# Resultado típico: center ~1450, width ~2800
```

**Valores promedio del dataset (calculados de 50 imágenes):**
```python
# Usar estos si quieres consistencia en todo el dataset
INBREAST_WINDOW_CENTER = 1450  # Ajustar según tu análisis
INBREAST_WINDOW_WIDTH = 2800
```

---

## 📖 Referencias

### DICOM Standard
- **Window Center/Width:** DICOM PS3.3 C.11.2.1.2 (VOI LUT Module)
- **Tag (0028,1050):** Window Center
- **Tag (0028,1051):** Window Width
- **Tag (0028,1056):** VOI LUT Function

### Papers
- InBreast Dataset: Moreira et al. (2012) "INbreast: toward a full-field digital mammographic database"
- VOI LUT: DICOM Standard Part 3, Section C.11.2

### Herramientas
- pydicom: https://pydicom.github.io/
- NumPy: https://numpy.org/
- Matplotlib: https://matplotlib.org/

---

## 🔗 Archivos Relacionados

En el proyecto:
- `../vendors/Siemens/inbreast_dicom_analysis.md` - Análisis completo de InBreast DICOM
- `../vendors/Siemens/technical_specifications_summary.md` - Especificaciones técnicas
- `../mammography_equipment.csv` - Base de datos de equipos

---

## ✅ TODO / Mejoras Futuras

- [ ] Implementar VOI LUT Sequence (tabla de lookup personalizada)
- [ ] Soporte para Presentation LUT
- [ ] Calcular windowing específico por región de interés (ROI)
- [ ] Detectar automáticamente tipo de vista (CC vs MLO) y ajustar
- [ ] Cache de valores calculados para dataset completo
- [ ] Interfaz gráfica para ajuste interactivo
- [ ] Exportar imágenes windowed a PNG/JPG

---

**Última actualización:** 4 de junio de 2026  
**Autor:** Dataset Preprocessing Project  
**Propósito:** Soporte para mamografía sin metadatos DICOM
