# SIEMENS MAMMOMAT - Technical Specifications Summary

**Last Updated:** June 4, 2026  
**Purpose:** Compilation of technical specifications for research and DICOM processing

---

## 1. KNOWN SPECIFICATIONS (From Research Datasets)

### MAMMOMAT MammoNovation (2008-2015)
**Source:** InBreast Dataset (2012)

#### Detector Specifications
- **Detector Type:** Solid-state detector of amorphous selenium (a-Se)
- **Pixel Size:** 70 μm (0.070 mm)
- **Bit Depth:** 14-bit contrast resolution
- **Matrix Size:** 
  - 3328 × 4084 pixels (primary configuration)
  - 2560 × 3328 pixels (alternative, depends on compression plate/breast size)
- **Detector Area:** Calculated ~23.3 × 28.6 cm (primary), ~17.9 × 23.3 cm (alternative)

#### Image Format
- **Format:** DICOM
- **Acquisition Period:** April 2008 - July 2010 (InBreast dataset)
- **Location:** Breast Centre, Centro Hospitalar de S. João, Porto, Portugal

#### Notes
- **Most complete specifications available** among all Siemens models in research datasets
- Full-field digital mammography (FFDM) system
- No tomosynthesis capability

---

### MAMMOMAT Inspiration (2012-2020)
**Sources:** NYU Dataset (2019), MBTST (2018), CMMD (2020), M-BIG (2023)

#### Detector Specifications
- **Detector Type:** DR (Digital Radiography)
- **Pixel Size:** ⚠️ NOT SPECIFIED in available datasets
- **Bit Depth:** 8-bit (NYU - after processing/cropping)
- **Matrix Size:** Multiple resolutions documented:
  - 2290 × 1890 pixels (NYU, most common)
  - 1458 × 1458 pixels (NYU, cropped)
  - 2677 × 1942 pixels (NYU)
  - 2294 × 1914 pixels (CMMD)
- **Detector Area:** Estimated ~24 × 30 cm (standard FFDM field)

#### Capabilities
- **Tomosynthesis:** Yes (DBT - Digital Breast Tomosynthesis)
- **2D Imaging:** Yes (FFDM)

#### Notes
- **Most widely adopted** Siemens model in research datasets (4 datasets)
- Used extensively 2010-2017 period
- Images often cropped/processed before dataset release (reduces technical detail availability)

---

### MAMMOMAT Novation DR (2008-2015)
**Source:** NYU Dataset (2019)

#### Detector Specifications
- **Detector Type:** DR (Digital Radiography)
- **Pixel Size:** ⚠️ NOT SPECIFIED
- **Bit Depth:** ⚠️ NOT SPECIFIED
- **Matrix Size:** 
  - 2290 × 1890 pixels
  - 1458 × 1458 pixels (cropped)
  - 2677 × 1942 pixels

#### Notes
- Digital Radiography version of MammoNovation
- Transition model between film-screen and full DR

---

## 2. MISSING CRITICAL SPECIFICATIONS

### For All Models - NEED FROM DATASHEETS:

#### DICOM Processing Parameters
- ⚠️ **VOI LUT (Value of Interest Look-Up Table)**
  - Window Center
  - Window Width
  - LUT Function (LINEAR, SIGMOID, etc.)
  
- ⚠️ **Pixel Spacing** (mm between pixel centers)
  - (0028,0030) DICOM tag value
  - Often different from physical pixel size due to calibration
  
- ⚠️ **Modality LUT**
  - (0028,3000) Transformation for rescaling pixel values
  
- ⚠️ **Presentation LUT**
  - (2050,0020) Display transformation parameters

#### Image Quality Parameters
- ⚠️ **MTF (Modulation Transfer Function)**
  - Spatial frequency response
  - Typically measured in lp/mm (line pairs per millimeter)
  
- ⚠️ **DQE (Detective Quantum Efficiency)**
  - Detector efficiency at different spatial frequencies
  - Usually measured at 0, 2, 4, 8 lp/mm
  
- ⚠️ **CNR (Contrast-to-Noise Ratio)**
  - Signal-to-noise performance
  
- ⚠️ **Dynamic Range**
  - Actual usable bit depth (may differ from stored bit depth)

#### X-Ray Specifications
- ⚠️ **kVp Range** (kilovolt peak)
- ⚠️ **mAs Range** (milliampere-seconds)
- ⚠️ **Anode Material** (typically Tungsten or Molybdenum)
- ⚠️ **Filter Materials** (Mo, Rh, Ag, etc.)
- ⚠️ **AEC (Automatic Exposure Control)** parameters

#### Geometric Parameters
- ⚠️ **SID (Source-to-Image Distance)**
- ⚠️ **Focal Spot Size** (small/large)
- ⚠️ **Magnification Factor** (if magnification views supported)

---

## 3. NEWER MODELS (2018-2026) - NO DATASET SPECIFICATIONS

### MAMMOMAT Revelation (2018-present)

#### Known Specifications (from marketing materials)
- **Detector Type:** Amorphous Selenium (a-Se)
- **Detector Size:** 24 × 30 cm
- **Tomosynthesis:** Yes (50° Wide-Angle)
- **Contrast Enhanced:** Yes (TiCEM)
- **Technologies:** PRIME, TomoFlow, Insight 2D/3D

#### NEEDED FROM DATASHEET:
- ✗ Pixel size (μm)
- ✗ Bit depth
- ✗ Exact matrix size (pixels)
- ✗ All DICOM parameters
- ✗ MTF/DQE specifications
- ✗ VOI LUT defaults

---

### MAMMOMAT B.brilliant (2024-2026)

#### Known Specifications (from marketing materials)
- **Detector Type:** Next-generation fast readout detector
- **Tomosynthesis:** Yes (50° Wide-Angle, 5 seconds)
- **Contrast Enhanced:** Yes (ClearCEM)
- **Technologies:** PlatinumTomo, Flying Focal Spot, PREMIA AI

#### NEEDED FROM DATASHEET:
- ✗ Pixel size (μm)
- ✗ Bit depth
- ✗ Matrix size (pixels)
- ✗ All DICOM parameters
- ✗ MTF/DQE specifications
- ✗ VOI LUT defaults

---

## 4. RECOMMENDED DOCUMENTATION TO OBTAIN

### Priority 1: Technical Datasheets (PDF)
**Where to find:**
- Siemens Healthineers website (requires registration)
- Medical equipment distributors
- Hospital purchasing departments
- FDA 510(k) clearance documents (public, but limited detail)

**Documents to search for:**
1. **Product Brochures** - Marketing specs (pixel size, bit depth, matrix)
2. **Technical Specifications Sheets** - Detailed detector specifications
3. **DICOM Conformance Statements** - DICOM tag implementations
4. **Service/User Manuals** - Comprehensive technical details (often restricted)

### Priority 2: Regulatory Documents
**FDA 510(k) Database:**
- Search: "MAMMOMAT" at https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm
- May contain: detector specs, image quality metrics, comparison data

**CE Mark Technical Files:**
- European regulatory submissions (harder to access)

### Priority 3: Scientific Literature
**Already have:** Papers in `papers/` folder
**Additional searches:**
- PubMed: "MAMMOMAT [model] technical specifications"
- Google Scholar: "[model] detector characterization"
- IEEE Xplore: Medical imaging conferences

### Priority 4: DICOM Sample Files
**Most valuable for VOI LUT research:**
- Obtain sample DICOM files from each model
- Extract metadata using `pydicom`:
  - (0028,3010) VOI LUT Sequence
  - (0028,1050) Window Center
  - (0028,1051) Window Width
  - (0028,0030) Pixel Spacing
  - (0018,1164) Imager Pixel Spacing

---

## 5. DICOM METADATA EXTRACTION CHECKLIST

### For each Siemens model, we need:

```python
# Essential DICOM tags for preprocessing
tags_needed = {
    # Pixel Data
    '(0028,0010)': 'Rows',
    '(0028,0011)': 'Columns',
    '(0028,0100)': 'Bits Allocated',
    '(0028,0101)': 'Bits Stored',
    '(0028,0102)': 'High Bit',
    '(0028,0103)': 'Pixel Representation',
    
    # Spacing
    '(0028,0030)': 'Pixel Spacing',  # [row_spacing, col_spacing] in mm
    '(0018,1164)': 'Imager Pixel Spacing',  # Physical detector pixel size
    
    # VOI LUT (Value of Interest)
    '(0028,1050)': 'Window Center',
    '(0028,1051)': 'Window Width',
    '(0028,1055)': 'Window Center & Width Explanation',
    '(0028,3010)': 'VOI LUT Sequence',
    
    # Modality LUT
    '(0028,3000)': 'Modality LUT Sequence',
    '(0028,1052)': 'Rescale Intercept',
    '(0028,1053)': 'Rescale Slope',
    
    # Presentation
    '(0028,0004)': 'Photometric Interpretation',
    '(2050,0020)': 'Presentation LUT Shape',
    
    # Equipment
    '(0008,0070)': 'Manufacturer',
    '(0008,1090)': 'Manufacturer Model Name',
    '(0018,1000)': 'Device Serial Number',
    '(0018,1020)': 'Software Versions',
}
```

---

## 6. COMPARISON: What We Have vs What We Need

| Model | Pixel Size | Bit Depth | Matrix | VOI LUT | DQE/MTF | X-Ray Params |
|-------|------------|-----------|--------|---------|---------|--------------|
| **MammoNovation** | ✓ 70μm | ✓ 14-bit | ✓ Complete | ✗ | ✗ | ✗ |
| **Inspiration** | ✗ | ⚠️ 8-bit* | ⚠️ Various | ✗ | ✗ | ✗ |
| **Novation DR** | ✗ | ✗ | ⚠️ Various | ✗ | ✗ | ✗ |
| **Revelation** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **B.brilliant** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

*Note: NYU dataset shows 8-bit after processing; original bit depth unknown

---

## 7. ACTION ITEMS

### Immediate Actions:
1. ✓ Document known specifications (this file)
2. ⏳ Search FDA 510(k) database for MAMMOMAT submissions
3. ⏳ Extract DICOM metadata from sample files (if available)
4. ⏳ Contact Siemens Healthineers for technical documentation

### Research Tasks:
1. ⏳ Search scientific literature for detector characterization studies
2. ⏳ Review existing DICOM files in datasets for metadata extraction
3. ⏳ Compare specifications across vendors (Hologic, GE, Fujifilm)

### Documentation Needs:
1. **URGENT:** VOI LUT parameters for proper image windowing
2. **HIGH:** Actual pixel spacing vs physical pixel size (calibration)
3. **HIGH:** Bit depth of raw images (before dataset processing)
4. **MEDIUM:** DQE/MTF curves for image quality assessment
5. **LOW:** X-ray technique factors (usually automatic, less critical for image analysis)

---

## 8. NOTES FOR PREPROCESSING

### Why These Specifications Matter:

**Pixel Size:**
- Affects spatial resolution calculations
- Required for converting pixels to physical dimensions (mm)
- Critical for CAD algorithm calibration

**Bit Depth:**
- Determines dynamic range of pixel values
- 14-bit (16384 levels) vs 8-bit (256 levels) significantly impacts detail
- Many datasets reduce bit depth for storage (lossy transformation)

**VOI LUT:**
- Defines how raw pixel values map to displayable intensities
- **Critical** for proper windowing/leveling in visualization
- Affects contrast and brightness perception
- Different manufacturers use different default curves

**Matrix Size:**
- Determines image resolution
- Larger matrices = more detail but larger file sizes
- Often downsampled/cropped in research datasets

**DQE/MTF:**
- Characterizes detector performance
- Useful for understanding dataset limitations
- Helps compare results across different equipment

---

## 9. USEFUL RESOURCES

### Siemens Official:
- https://www.siemens-healthineers.com/mammography
- Product pages for each model
- DICOM Conformance Statements (if publicly available)

### Regulatory:
- FDA 510(k) Database: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm
- Search term: "MAMMOMAT"

### Scientific:
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- Google Scholar: https://scholar.google.com/
- IEEE Xplore: https://ieeexplore.ieee.org/

### DICOM Resources:
- DICOM Standard: https://www.dicomstandard.org/
- pydicom documentation: https://pydicom.github.io/
- DICOM tag browser: https://dicom.innolitics.com/

---

## SUMMARY

**Status:** Partial specifications available  
**Best documented model:** MAMMOMAT MammoNovation (InBreast dataset)  
**Most common model in research:** MAMMOMAT Inspiration  
**Biggest gap:** VOI LUT parameters and raw bit depth values  
**Next step:** Obtain official datasheets or analyze DICOM files directly
