# SIEMENS MAMMOMAT - Documents to Obtain

## PRIORITY DOCUMENTS CHECKLIST

### 📋 MAMMOMAT MammoNovation (2008-2015)

**Status:** ✓ Basic specs available from InBreast dataset  
**Still need:**

- [ ] **DICOM Conformance Statement** - For VOI LUT implementation
- [ ] **Technical Datasheet/Brochure** - Verify 70μm pixel size, confirm a-Se detector specs
- [ ] **FDA 510(k) Summary** - Search K070234 or similar
- [ ] **Service Manual** (if accessible) - Complete technical specifications
- [ ] **Application Guide** - Recommended imaging protocols

**Suggested filenames to search:**
- `MAMMOMAT_MammoNovation_Datasheet.pdf`
- `Siemens_MammoNovation_DICOM_Conformance.pdf`
- `MammoNovation_Technical_Specifications.pdf`

---

### 📋 MAMMOMAT Inspiration (2012-2020)

**Status:** ⚠️ Used in many datasets but limited technical details  
**Critically need:**

- [ ] **Technical Datasheet/Brochure** - Pixel size, bit depth, detector specs
- [ ] **DICOM Conformance Statement** - VOI LUT, pixel spacing tags
- [ ] **DBT Technical Specifications** - Tomosynthesis angle, projections count
- [ ] **FDA 510(k) Summary** - Search "Inspiration" submissions
- [ ] **Detector Characterization Study** - DQE/MTF curves

**Suggested filenames to search:**
- `MAMMOMAT_Inspiration_Datasheet.pdf`
- `Inspiration_DBT_Technical_Specifications.pdf`
- `Siemens_Inspiration_DICOM_Conformance.pdf`

**Known FDA submissions:**
- Search FDA database for K113227 (DBT upgrade) or similar

---

### 📋 MAMMOMAT Revelation (2018-present)

**Status:** ⚠️ Only marketing information available  
**Need:**

- [ ] **Product Brochure** - Full technical specifications
- [ ] **DICOM Conformance Statement** - PRIME technology DICOM implementation
- [ ] **TiCEM Technical Guide** - Contrast-enhanced imaging parameters
- [ ] **50° Wide-Angle DBT Specs** - Tomosynthesis technical details
- [ ] **Detector Specifications** - a-Se detector characteristics
- [ ] **FDA 510(k) Summary** - Recent submission for US market

**Suggested filenames to search:**
- `MAMMOMAT_Revelation_Brochure.pdf`
- `Revelation_PRIME_Technology.pdf`
- `TiCEM_Contrast_Enhanced_Mammography.pdf`
- `Revelation_DBT_Technical_Specifications.pdf`

**Known features to document:**
- PRIME Technology (artifact reduction)
- TomoFlow (DBT workflow)
- Insight 2D/3D (synthetic imaging)
- 50° wide-angle tomosynthesis

---

### 📋 MAMMOMAT B.brilliant (2024-2026)

**Status:** ⚠️ Newest model, minimal technical docs publicly available  
**Need:**

- [ ] **Product Brochure** (2024+) - Latest specifications
- [ ] **DICOM Conformance Statement** - Current implementation
- [ ] **ClearCEM Technical Guide** - New contrast-enhanced imaging
- [ ] **PlatinumTomo Specifications** - 5-second tomosynthesis details
- [ ] **PREMIA AI Documentation** - AI reconstruction algorithms
- [ ] **Flying Focal Spot Technology** - Technical description

**Suggested filenames to search:**
- `MAMMOMAT_B_brilliant_Brochure_2024.pdf`
- `B_brilliant_ClearCEM_Guide.pdf`
- `PlatinumTomo_Technical_Specifications.pdf`
- `PREMIA_AI_Reconstruction.pdf`

**Known features to document:**
- PlatinumTomo (fast DBT)
- Flying Focal Spot (enhanced resolution)
- PREMIA AI (image reconstruction)
- ComfortPackage (patient experience)
- ClearCEM (contrast imaging)

---

## WHERE TO SEARCH FOR DOCUMENTS

### 1. Siemens Healthineers Official Website

**Direct access (may require registration):**
```
https://www.siemens-healthineers.com/mammography/digital-mammography-systems/
```

**Marketing assets domain:**
```
https://marketing.webassets.siemens-healthineers.com/
```

**Documentation portal (if you have access):**
```
https://www.healthcare.siemens.com/medical-imaging-it/
```

**Note:** Many technical documents require:
- Healthcare professional verification
- Hospital/institution email
- Registration with Siemens customer portal

---

### 2. FDA 510(k) Database

**Search URL:**
```
https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm
```

**Search terms:**
- "MAMMOMAT MammoNovation"
- "MAMMOMAT Inspiration"
- "MAMMOMAT Revelation"
- "MAMMOMAT B.brilliant"
- "Siemens" + "digital mammography"

**What you'll find:**
- Device classification
- Predicate devices
- Indications for use
- Limited technical specifications
- Comparison to previous models

**Known 510(k) numbers (to verify):**
- K113227 - Possible Inspiration DBT
- Search "Siemens Medical Solutions" or "Siemens Healthineers" as applicant

---

### 3. DICOM Conformance Statements

**Where to look:**
- Siemens Medical Customer Portal (requires login)
- Hospital PACS administrators (they should have copies)
- Medical physics departments
- DICOM standard website might list some

**What they contain:**
- Supported DICOM SOP Classes
- Tag implementations
- VOI LUT specifications
- Modality LUT details
- Transfer syntaxes

**Typical filename format:**
```
[Model]_DICOM_Conformance_Statement_v[version].pdf
```

---

### 4. Scientific Literature Search

**PubMed search strings:**
```
"MAMMOMAT MammoNovation" AND (specifications OR detector OR characterization)
"MAMMOMAT Inspiration" AND (technical OR DQE OR MTF)
"Siemens mammography" AND (detector OR selenium OR pixel)
```

**Google Scholar:**
```
MAMMOMAT technical specifications filetype:pdf
Siemens mammography detector characterization
amorphous selenium mammography Siemens specifications
```

**ResearchGate:**
- Search for researchers who published papers using Siemens equipment
- Request technical specifications documents directly

---

### 5. Equipment Distributors

**May have access to:**
- Product brochures
- Technical datasheets
- Comparison charts
- Application guides

**Contact:**
- Local Siemens Healthineers representatives
- Medical equipment distributors in your region
- Hospital purchasing departments

---

### 6. Medical Physics Resources

**Organizations that may have specs:**
- **AAPM** (American Association of Physicists in Medicine)
- **EFOMP** (European Federation of Organisations for Medical Physics)
- Medical physics departments at hospitals

**Resources:**
- Equipment evaluation reports
- Acceptance testing protocols
- QA/QC documentation
- Detector characterization studies

---

## SPECIFIC DOCUMENTS WE NEED

### Essential (Priority 1):

1. **DICOM Conformance Statements** for each model
   - Contains: VOI LUT, Pixel Spacing, Modality LUT implementations
   - Format: PDF, typically 50-200 pages
   - **Why critical:** Essential for proper DICOM processing

2. **Technical Datasheets** (Product Specifications)
   - Contains: Pixel size, bit depth, matrix size, detector type
   - Format: PDF brochure, 2-10 pages
   - **Why critical:** Baseline specifications for research

3. **FDA 510(k) Summaries**
   - Contains: Device description, technical characteristics, clinical data
   - Format: PDF, publicly available
   - **Why critical:** Regulatory validation of specifications

### Important (Priority 2):

4. **Detector Characterization Reports**
   - Contains: DQE curves, MTF curves, NPS (Noise Power Spectrum)
   - Source: Scientific papers, medical physics reports
   - **Why important:** Image quality assessment

5. **Application Guides / User Manuals**
   - Contains: Imaging protocols, technique factors, recommended settings
   - Format: PDF, often restricted
   - **Why important:** Understanding acquisition parameters

6. **Service Manuals** (if accessible)
   - Contains: Complete technical specifications, calibration procedures
   - Format: PDF, usually restricted to service engineers
   - **Why important:** Most comprehensive technical details

---

## SAMPLE DICOM FILE ALTERNATIVE

**If datasheets unavailable, obtain sample DICOM files:**

### What we can extract from DICOM headers:

```bash
# Using pydicom to extract specifications
python extract_dicoms.py --extract-metadata --vendor Siemens --model Inspiration

# Key information from DICOM:
- (0028,0030) Pixel Spacing → Physical spacing in mm
- (0018,1164) Imager Pixel Spacing → Detector pixel size
- (0028,0100-0103) Bit depth tags
- (0028,1050-1051) Window Center/Width (VOI LUT)
- (0018,1000) Device Serial Number
- (0018,1020) Software Version
```

**Sources for sample DICOMs:**
- InBreast dataset (has Siemens MammoNovation)
- NYU dataset (has Siemens Inspiration)
- Collaborating hospitals
- TCIA (The Cancer Imaging Archive)

---

## LEGAL CONSIDERATIONS

### ⚠️ Important Notes:

**Publicly Available:**
- Marketing brochures
- FDA 510(k) summaries
- Published scientific papers
- Conference proceedings

**May Require Registration:**
- Technical datasheets
- DICOM Conformance Statements
- Application guides

**Restricted Access:**
- Service manuals (proprietary)
- Detailed software documentation
- Calibration procedures
- Some clinical validation reports

**Fair Use for Research:**
- Using specifications for academic research is generally acceptable
- Cite sources appropriately
- Do not redistribute restricted documents publicly

---

## CONTACT STRATEGY

### If official channels don't work:

1. **Contact researchers** who published papers using Siemens equipment
   - Ask if they have technical specifications
   - Many are willing to share for research purposes

2. **Medical physics mailing lists**
   - AAPM forums
   - MedPhys communities
   - ResearchGate questions

3. **Hospital collaborations**
   - Clinical collaborators may have access
   - Medical physicists often maintain equipment documentation

4. **Direct Siemens contact**
   - Explain research purpose
   - Request technical specifications for academic use
   - May require institutional email/affiliation

---

## QUICK REFERENCE: Priority by Model

| Model | Priority | Reason |
|-------|----------|---------|
| **MammoNovation** | MEDIUM | Already have good specs from InBreast; need DICOM details |
| **Inspiration** | **HIGH** | Most used in datasets; missing critical specs |
| **Revelation** | MEDIUM | Current system; useful for modern data |
| **B.brilliant** | LOW | Too new; likely not in research datasets yet |

---

## NEXT STEPS

1. ✅ Start with **FDA 510(k) database search** (free, public)
2. ✅ Extract **DICOM metadata** from existing dataset files (InBreast, NYU)
3. ✅ Search **PubMed/Google Scholar** for technical papers
4. ⏳ Request documents from **Siemens Healthineers** (may require registration)
5. ⏳ Contact **research collaborators** who use Siemens equipment

---

**Last Updated:** June 4, 2026  
**Next Review:** After obtaining first set of official documents
