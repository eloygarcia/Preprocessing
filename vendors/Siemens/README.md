# Siemens MAMMOMAT - Technical Documentation

This folder contains technical documentation and tools for Siemens MAMMOMAT mammography systems.

## 📁 Contents

### Documentation Files

#### 1. `technical_specifications_summary.md` (📊 Comprehensive)
**Purpose:** Complete technical specifications compilation  
**Contents:**
- Known specifications from research datasets (InBreast, NYU, CMMD, M-BIG)
- Missing specifications checklist
- DICOM parameter requirements (VOI LUT, Pixel Spacing, etc.)
- Comparison table across all models
- Action items and next steps

**Use this when:**
- You need detailed technical specs for preprocessing
- Planning DICOM processing pipelines
- Understanding dataset limitations
- Comparing models across research studies

**Key sections:**
- Section 1: Known specifications (what we have)
- Section 2: Missing specifications (what we need)
- Section 6: Comparison table
- Section 7: Action items

---

#### 2. `documents_to_obtain.md` (🔍 Search Guide)
**Purpose:** Practical guide for finding official documentation  
**Contents:**
- Checklist of documents needed for each model
- Where to search (FDA, Siemens website, literature)
- Specific filenames to look for
- Contact strategies
- Legal considerations

**Use this when:**
- Searching for official datasheets
- Need FDA 510(k) information
- Looking for DICOM Conformance Statements
- Contacting Siemens or researchers for specs

**Priority documents:**
1. DICOM Conformance Statements (for VOI LUT)
2. Technical Datasheets (for pixel size, bit depth)
3. FDA 510(k) Summaries (regulatory specs)

---

### Tools

#### 3. `extract_dicom_specs.py` (🔧 Python Script)
**Purpose:** Extract technical specifications from DICOM files  
**Language:** Python 3  
**Dependencies:** `pydicom`

**What it does:**
- Scans DICOM files and extracts technical metadata
- Groups specifications by equipment model
- Generates summary reports (JSON or Markdown)
- Calculates pixel size in micrometers from DICOM spacing tags

**Usage:**

```bash
# Install dependency first
pip install pydicom

# Extract Siemens specs from InBreast dataset
python extract_dicom_specs.py /path/to/InBreast --vendor Siemens

# Save to JSON report
python extract_dicom_specs.py /path/to/dicoms --vendor Siemens --output siemens_specs.json

# Save to Markdown report
python extract_dicom_specs.py /path/to/dicoms --vendor Siemens --output siemens_specs.md --format markdown
```

**Extracts:**
- Pixel size (μm) from ImagerPixelSpacing or PixelSpacing tags
- Bit depth (BitsStored, BitsAllocated)
- Matrix size (Rows, Columns)
- VOI LUT parameters (WindowCenter, WindowWidth)
- Modality LUT (RescaleIntercept, RescaleSlope)
- Equipment info (Model, Serial Number, Software Version)
- Acquisition parameters (kVp, Exposure, Compression Force)

**Output formats:**
- Console: Formatted summary table
- JSON: Machine-readable specifications
- Markdown: Human-readable report

---

## 🎯 Quick Start Guide

### If you have DICOM files from Siemens equipment:

**Step 1:** Extract specifications from your DICOM files
```bash
cd vendors/Siemens
python extract_dicom_specs.py /path/to/your/dicoms --vendor Siemens --output extracted_specs.json
```

**Step 2:** Compare with known specifications
- Open `technical_specifications_summary.md`
- Go to Section 1 for your model
- Compare pixel size, bit depth, matrix size

**Step 3:** Check for missing parameters
- See Section 2 in `technical_specifications_summary.md`
- Verify if your DICOMs have VOI LUT parameters
- Note any gaps in your extracted data

---

### If you need official datasheets:

**Step 1:** Identify what you need
- Open `documents_to_obtain.md`
- Find checklist for your model (MammoNovation, Inspiration, Revelation, B.brilliant)

**Step 2:** Search FDA database
```
Go to: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm
Search: "MAMMOMAT [your model]"
```

**Step 3:** Search literature
```
PubMed: "MAMMOMAT [model] specifications"
Google Scholar: "Siemens [model] detector characterization"
```

**Step 4:** Contact sources
- See "Contact Strategy" section in `documents_to_obtain.md`
- Researchers, medical physicists, Siemens representatives

---

## 📊 Models Covered

### MammoNovation (2008-2015)
- ✅ **Best documented** (InBreast dataset)
- ✅ Pixel size: 70 μm
- ✅ Bit depth: 14-bit
- ✅ Matrix: 3328×4084 or 2560×3328
- ⚠️ Need: VOI LUT parameters

### MAMMOMAT Inspiration (2012-2020)
- ⚠️ **Most used but underspecified**
- ❌ Pixel size: Unknown
- ⚠️ Bit depth: Unknown (8-bit after processing in NYU)
- ⚠️ Matrix: Multiple sizes (2290×1890, 2294×1914, etc.)
- ❌ Need: All original specifications

### MAMMOMAT Revelation (2018-present)
- ⚠️ **Current system, minimal dataset presence**
- ✅ Detector: a-Se (24×30 cm)
- ❌ Pixel size: Unknown
- ❌ Bit depth: Unknown
- ❌ Matrix: Unknown
- ❌ Need: Complete technical specs

### MAMMOMAT B.brilliant (2024-2026)
- ⚠️ **Newest system, not in research datasets yet**
- ⚠️ Detector: Next-gen fast readout
- ❌ All specifications unknown
- ❌ Need: Official datasheets

---

## 🔬 Research Datasets Using Siemens Equipment

### Primary Datasets:
1. **InBreast** (2012) - MammoNovation - 🌟 Best specs
2. **NYU** (2019) - Inspiration + Novation DR - Large dataset
3. **CMMD** (2020) - Inspiration - Chinese dataset
4. **M-BIG** (2023) - Inspiration - Swedish, DBT focus
5. **MBTST** (2018) - Inspiration - DBT trial

### See Also:
- `../../mammography_equipment.csv` - All equipment across datasets
- `../../mammography_equipment_specifications.md` - Detailed specs from PDFs
- `../siemens.md` - Model descriptions and timeline
- `../siemens_models.csv` - Summary table

---

## 🎯 Why These Specifications Matter

### For Image Processing:
- **Pixel Size:** Required for converting pixels to physical dimensions (mm)
- **Bit Depth:** Determines dynamic range and quantization levels
- **Matrix Size:** Affects resolution and file size

### For DICOM Processing:
- **VOI LUT:** Critical for proper windowing and display
- **Pixel Spacing:** Needed for spatial measurements
- **Modality LUT:** Required for rescaling pixel values to Hounsfield Units or optical density

### For Research Comparisons:
- Compare results across different equipment
- Account for detector differences in CAD algorithms
- Validate findings across manufacturer specifications

### For Dataset Documentation:
- Properly cite equipment specifications
- Enable reproducibility
- Document preprocessing requirements

---

## ⚠️ Known Limitations

### What We Have:
- ✅ Basic specifications from InBreast (MammoNovation)
- ✅ Matrix sizes from multiple datasets
- ✅ General detector types (a-Se, DR)

### What We're Missing:
- ❌ **VOI LUT parameters** for all models (critical!)
- ❌ Original bit depth before dataset processing
- ❌ Exact pixel size for Inspiration model
- ❌ DQE/MTF curves (image quality metrics)
- ❌ X-ray technique parameters
- ❌ Complete specs for newer models (Revelation, B.brilliant)

### Why Data is Limited:
1. Research datasets often preprocess images (downsample, convert bit depth)
2. DICOM metadata may be stripped for anonymization
3. Technical specifications in papers are often incomplete
4. Official datasheets require registration/purchase
5. Newer equipment not yet in public research datasets

---

## 📝 Next Steps

### Immediate (High Priority):
1. ✅ Run `extract_dicom_specs.py` on InBreast dataset
2. ⏳ Search FDA 510(k) database for each model
3. ⏳ Extract DICOM metadata from NYU dataset (if available)
4. ⏳ Search PubMed for detector characterization papers

### Short-term (Medium Priority):
1. ⏳ Contact Siemens for technical datasheets
2. ⏳ Request DICOM Conformance Statements
3. ⏳ Connect with researchers who published using Siemens equipment
4. ⏳ Check medical physics resources (AAPM, EFOMP)

### Long-term (Lower Priority):
1. ⏳ Obtain service manuals (if accessible)
2. ⏳ Conduct detector characterization studies (if equipment available)
3. ⏳ Document findings in research papers
4. ⏳ Contribute specifications back to research community

---

## 🔗 Useful Links

### Official Resources:
- **Siemens Healthineers:** https://www.siemens-healthineers.com/mammography
- **FDA Device Database:** https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm
- **DICOM Standard:** https://www.dicomstandard.org/

### Tools:
- **pydicom Documentation:** https://pydicom.github.io/
- **DICOM Tag Browser:** https://dicom.innolitics.com/
- **DICOM Viewer:** (consider Horos, 3D Slicer, or RadiAnt)

### Research:
- **PubMed:** https://pubmed.ncbi.nlm.nih.gov/
- **Google Scholar:** https://scholar.google.com/
- **IEEE Xplore:** https://ieeexplore.ieee.org/

---

## 📧 Contributing

If you obtain additional specifications or datasheets:

1. Add specifications to `technical_specifications_summary.md`
2. Update the "KNOWN SPECIFICATIONS" section
3. Move items from "MISSING" to "KNOWN"
4. Document the source (paper, datasheet, DICOM extraction)
5. Update comparison tables

---

## 📄 File Status

| File | Size | Status | Last Updated |
|------|------|--------|--------------|
| technical_specifications_summary.md | ~30 KB | ✅ Complete | June 4, 2026 |
| documents_to_obtain.md | ~20 KB | ✅ Complete | June 4, 2026 |
| extract_dicom_specs.py | ~20 KB | ✅ Complete | June 4, 2026 |
| README.md | This file | ✅ Complete | June 4, 2026 |

---

**Last Updated:** June 4, 2026  
**Maintainer:** Dataset preprocessing project  
**Purpose:** Support mammography image preprocessing research
