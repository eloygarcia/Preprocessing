# InBreast Dataset - DICOM Analysis Report

**Date:** June 4, 2026  
**Dataset:** INbreast (Portuguese database)  
**Files Analyzed:** 410 DICOM files  
**Location:** `/home/eloygarcia/Escritorio/Datasets/INbreast/AllDICOMs/`

---

## 🔍 Key Findings

### Critical Discovery: Files Were Re-Generated with MATLAB

The DICOM files in the InBreast dataset are **NOT original equipment DICOMs**.

**Evidence:**
```
Modality: OT (Other) - NOT "MG" (Mammography)
Conversion Type: WSD (Workstation)
Secondary Capture Device Manufacturer: The MathWorks
Secondary Capture Device Model: MATLAB
```

**Implication:**  
The dataset authors took the original Siemens MAMMOMAT images, processed them in MATLAB for anonymization, and re-exported them as "Secondary Capture" DICOM files. This process **eliminated all original equipment metadata**.

---

## ✅ Specifications Available from DICOM Files

### Image Parameters (Preserved)

| Parameter | Value | Status |
|-----------|-------|--------|
| **Rows × Columns** | 3328×4084, 2560×3328 pixels | ✓ Confirmed |
| **Bits Allocated** | 16 bits | ✓ Available |
| **Bits Stored** | 16 bits | ⚠️ Upsampled from 14-bit |
| **High Bit** | 15 | ✓ Available |
| **Photometric Interpretation** | MONOCHROME2 | ✓ Standard |
| **Largest Pixel Value** | ~2970 | 💡 ~12 bits actually used |

**Note on Bit Depth:**  
- Original equipment: 14-bit (as stated in InBreast paper)
- DICOM files: 16-bit (padded during MATLAB export)
- Actual dynamic range: ~12 bits based on max pixel value (~2970 < 4096)

---

## ❌ Specifications Lost in Anonymization

### Equipment Information (Critical Loss)

| DICOM Tag | Name | Status | Impact |
|-----------|------|--------|--------|
| (0008,0070) | Manufacturer | ❌ Removed | Lost "Siemens" |
| (0008,1090) | Model Name | ❌ Removed | Lost "MammoNovation" |
| (0018,1000) | Serial Number | ❌ Removed | Cannot track device |
| (0018,1020) | Software Version | ❌ Removed | Cannot verify algorithms |

### Spatial Information (CRITICAL LOSS ⭐)

| DICOM Tag | Name | Status | Impact |
|-----------|------|--------|--------|
| (0028,0030) | **Pixel Spacing** | ❌ Removed | **Cannot convert pixels to mm** |
| (0018,1164) | **Imager Pixel Spacing** | ❌ Removed | **Lost 70 μm specification** |

**Workaround:**  
Must use pixel size from InBreast paper: **70 μm = 0.070 mm**

### Display Parameters (Important Loss)

| DICOM Tag | Name | Status | Impact |
|-----------|------|--------|--------|
| (0028,1050) | Window Center | ❌ Removed | Must compute manually |
| (0028,1051) | Window Width | ❌ Removed | Must compute manually |
| (0028,1052) | Rescale Intercept | ❌ Removed | No intensity calibration |
| (0028,1053) | Rescale Slope | ❌ Removed | No intensity calibration |

### Clinical Information (Complete Loss)

| DICOM Tag | Name | Status | Impact |
|-----------|------|--------|--------|
| (0018,5101) | View Position | ❌ Removed | Lost CC/MLO info* |
| (0020,0060) | Laterality | ❌ Removed | Lost L/R info* |
| (0018,0060) | kVp | ❌ Removed | No X-ray technique data |
| (0018,1152) | Exposure (mAs) | ❌ Removed | No dose information |
| (0018,11A2) | Compression Force | ❌ Removed | No compression data |

*Note: View position and laterality are encoded in filenames (e.g., `MG_L_CC_ANON.dcm`)

---

## 📊 Statistics from 410 Files

### Matrix Size Distribution
- **3328 × 4084 pixels:** ~50% of files (larger breasts)
- **2560 × 3328 pixels:** ~50% of files (smaller breasts/compressions)

### Image Characteristics
- **Samples per Pixel:** 1 (grayscale)
- **Pixel Representation:** Unsigned integer (0)
- **Smallest Pixel Value:** 0
- **Largest Pixel Value:** ~2970 (varies by image)
- **SOP Class:** Digital Mammography X-Ray Image Storage

---

## 🔧 Practical Implications for Preprocessing

### What We Can Do:

1. ✅ **Matrix size is correct** - Use rows/columns from DICOM
2. ✅ **Pixel values are preserved** - Original intensities (probably)
3. ✅ **Files are properly formatted** - Can be read with pydicom/SimpleITK

### What We Must Do Manually:

1. ⚠️ **Add pixel spacing manually:** Set to 0.070 mm (70 μm) from paper
2. ⚠️ **Compute window/level:** Calculate from histogram/statistics
3. ⚠️ **Parse filenames:** Extract view (CC/MLO) and laterality (L/R)
4. ⚠️ **Use paper specifications:** For any equipment-related parameters

### Recommended Code Pattern:

```python
import pydicom
import numpy as np

# Read DICOM (no metadata for spacing!)
dcm = pydicom.dcmread(filepath)
image = dcm.pixel_array

# MANUALLY set pixel spacing (from InBreast paper)
PIXEL_SIZE_MM = 0.070  # 70 μm
pixel_spacing = [PIXEL_SIZE_MM, PIXEL_SIZE_MM]

# Compute window/level from image statistics
window_center = np.median(image[image > 0])
window_width = np.percentile(image, 99) - np.percentile(image, 1)

# Parse view and laterality from filename
# Format: *_MG_{L|R}_{CC|ML}_ANON.dcm
import re
match = re.search(r'MG_([LR])_(CC|ML)', filepath)
if match:
    laterality = match.group(1)  # 'L' or 'R'
    view = match.group(2)  # 'CC' or 'ML' (MLO)
```

---

## 📚 Where to Get Missing Specifications

Since DICOM metadata was stripped, we must rely on:

### 1. InBreast Paper (Primary Source)
**Reference:** Moreira et al. (2012) "INbreast: toward a full-field digital mammographic database"

**Specifications stated:**
- **Equipment:** Siemens MammoNovation FFDM
- **Detector:** Amorphous selenium (a-Se)
- **Pixel size:** 70 μm
- **Bit depth:** 14-bit (though stored as 16-bit in DICOMs)
- **Matrix sizes:** 3328×4084, 2560×3328 pixels
- **Detector area:** ~23.3 × 28.6 cm, ~17.9 × 23.3 cm

### 2. Siemens MAMMOMAT MammoNovation Datasheets
See: `documents_to_obtain.md` for search strategies

### 3. FDA 510(k) Database
Search for: "MAMMOMAT MammoNovation" or "Siemens mammography"

### 4. Scientific Literature
- Detector characterization studies
- Medical physics papers
- Equipment evaluation reports

---

## 🎯 Recommendations

### For Current Work:
1. ✅ Use specifications from InBreast paper (70 μm pixel size)
2. ✅ Compute window/level from image statistics
3. ✅ Parse clinical info from filenames
4. ✅ Document that spatial measurements depend on paper specs

### For Future Datasets:
1. ⚠️ **Check if DICOMs are original or re-generated**
   - Look for "Secondary Capture Device"
   - Check if Manufacturer is present
2. ⚠️ **Request original DICOMs if possible**
   - Contact dataset authors
   - Explain need for equipment metadata
3. ⚠️ **Obtain equipment specifications separately**
   - From papers, datasheets, or FDA database
   - Document assumptions clearly

### For Documentation:
1. ✅ Document that InBreast DICOMs are MATLAB re-exports
2. ✅ Note which specifications come from paper vs DICOM
3. ✅ List assumptions about pixel spacing
4. ✅ Explain limitations for spatial measurements

---

## 📁 Files Generated

- `inbreast_dicom_analysis.json` - Machine-readable report
- `inbreast_dicom_analysis.md` - This human-readable report (if saved)

---

## 🔗 Related Documentation

- `technical_specifications_summary.md` - Complete Siemens specs compilation
- `documents_to_obtain.md` - How to find official datasheets
- `../../mammography_equipment_specifications.md` - Specs from all datasets
- `../../papers/[2012] - InBreast.txt` - Original paper text

---

## ✅ Conclusion

**InBreast DICOM Analysis Summary:**

| Aspect | Status | Solution |
|--------|--------|----------|
| Matrix size | ✅ Available | Use from DICOM |
| Bit depth | ⚠️ Modified | Use 14-bit from paper |
| Pixel spacing | ❌ Missing | Use 70 μm from paper |
| VOI LUT | ❌ Missing | Compute from statistics |
| Equipment info | ❌ Missing | Use from paper |
| View/Laterality | ❌ Missing | Parse from filename |

**Key Takeaway:**  
InBreast DICOMs were re-generated with MATLAB, losing all original equipment metadata. Must rely on paper specifications for critical parameters like pixel size (70 μm).

---

**Analysis Date:** June 4, 2026  
**Analyst:** DICOM Specifications Extractor v1.0  
**Next Steps:** Check other datasets (NYU, CMMD) to see if they preserved more metadata
