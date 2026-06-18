#!/usr/bin/env python3
"""
DICOM Technical Specifications Extractor for Siemens MAMMOMAT
==============================================================

Extract technical specifications from DICOM files for documentation purposes.

Usage:
    python extract_dicom_specs.py /path/to/dicom/files --vendor Siemens
    python extract_dicom_specs.py /path/to/dicom/files --output specs_report.json

This script extracts:
- Detector specifications (pixel size, bit depth, matrix size)
- VOI LUT parameters (window center, width)
- Equipment information (model, serial number, software version)
- Image acquisition parameters
"""

import os
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any

try:
    import pydicom
    from pydicom.errors import InvalidDicomError
except ImportError:
    print("Error: pydicom is required. Install with: pip install pydicom")
    sys.exit(1)


class DicomSpecsExtractor:
    """Extract technical specifications from DICOM files."""
    
    # DICOM tags of interest
    TAGS_OF_INTEREST = {
        # Equipment Information
        'manufacturer': (0x0008, 0x0070),
        'manufacturer_model': (0x0008, 0x1090),
        'device_serial_number': (0x0018, 0x1000),
        'software_versions': (0x0018, 0x1020),
        'station_name': (0x0008, 0x1010),
        
        # Detector/Image Specifications
        'rows': (0x0028, 0x0010),
        'columns': (0x0028, 0x0011),
        'bits_allocated': (0x0028, 0x0100),
        'bits_stored': (0x0028, 0x0101),
        'high_bit': (0x0028, 0x0102),
        'pixel_representation': (0x0028, 0x0103),
        
        # Spacing
        'pixel_spacing': (0x0028, 0x0030),  # [row_spacing, col_spacing] in mm
        'imager_pixel_spacing': (0x0018, 0x1164),  # Physical detector pixel size
        
        # VOI LUT (Windowing)
        'window_center': (0x0028, 0x1050),
        'window_width': (0x0028, 0x1051),
        'window_explanation': (0x0028, 0x1055),
        
        # Modality LUT
        'rescale_intercept': (0x0028, 0x1052),
        'rescale_slope': (0x0028, 0x1053),
        'rescale_type': (0x0028, 0x1054),
        
        # Presentation
        'photometric_interpretation': (0x0028, 0x0004),
        
        # Acquisition Parameters
        'kvp': (0x0018, 0x0060),  # Peak kilovoltage
        'exposure_time': (0x0018, 0x1150),  # Exposure time in ms
        'exposure': (0x0018, 0x1152),  # Exposure in mAs
        'anode_target_material': (0x0018, 0x1191),
        'filter_material': (0x0018, 0x7050),
        'compression_force': (0x0018, 0x11A2),
        'body_part_thickness': (0x0018, 0x11A0),
        
        # Study/Series
        'modality': (0x0008, 0x0060),
        'series_description': (0x0008, 0x103E),
        'view_position': (0x0018, 0x5101),  # CC, MLO, etc.
        'laterality': (0x0020, 0x0060),  # L or R
    }
    
    def __init__(self, vendor_filter: Optional[str] = None):
        """
        Initialize the extractor.
        
        Args:
            vendor_filter: Only process files from this manufacturer (e.g., "Siemens")
        """
        self.vendor_filter = vendor_filter
        self.specs_by_model = defaultdict(lambda: defaultdict(list))
        self.file_count = 0
        self.error_count = 0
        
    def extract_from_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Extract specifications from a single DICOM file.
        
        Args:
            filepath: Path to DICOM file
            
        Returns:
            Dictionary of extracted specifications, or None if error
        """
        try:
            dcm = pydicom.dcmread(filepath, stop_before_pixels=True)
            
            # Check vendor filter
            manufacturer = str(dcm.get('Manufacturer', '')).strip()
            if self.vendor_filter and self.vendor_filter.lower() not in manufacturer.lower():
                return None
            
            # Extract all tags of interest
            specs = {}
            for name, tag in self.TAGS_OF_INTEREST.items():
                if tag in dcm:
                    value = dcm[tag].value
                    # Convert to JSON-serializable format
                    if isinstance(value, (list, tuple)):
                        value = [str(v) for v in value]
                    elif hasattr(value, 'decode'):  # bytes
                        value = value.decode('utf-8', errors='ignore')
                    else:
                        value = str(value)
                    specs[name] = value
            
            # Calculate pixel size in micrometers if spacing available
            if 'imager_pixel_spacing' in specs:
                try:
                    spacing = dcm.ImagerPixelSpacing
                    pixel_size_mm = float(spacing[0])  # Assume square pixels
                    specs['pixel_size_um'] = round(pixel_size_mm * 1000, 2)  # Convert mm to μm
                except (ValueError, IndexError):
                    pass
            elif 'pixel_spacing' in specs:
                try:
                    spacing = dcm.PixelSpacing
                    pixel_size_mm = float(spacing[0])
                    specs['pixel_size_um'] = round(pixel_size_mm * 1000, 2)
                except (ValueError, IndexError):
                    pass
            
            # Add filename for reference
            specs['source_file'] = filepath.name
            
            self.file_count += 1
            return specs
            
        except InvalidDicomError:
            # Not a DICOM file
            return None
        except Exception as e:
            print(f"Warning: Error processing {filepath.name}: {e}")
            self.error_count += 1
            return None
    
    def extract_from_directory(self, directory: Path, recursive: bool = True) -> None:
        """
        Extract specifications from all DICOM files in a directory.
        
        Args:
            directory: Path to directory containing DICOM files
            recursive: If True, search subdirectories recursively
        """
        print(f"Scanning directory: {directory}")
        
        # Find all potential DICOM files
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.glob('*'))
        
        # Filter to files only (not directories)
        files = [f for f in files if f.is_file()]
        
        print(f"Found {len(files)} files to check...")
        
        for filepath in files:
            specs = self.extract_from_file(filepath)
            if specs:
                model = specs.get('manufacturer_model', 'Unknown Model')
                
                # Group by model
                self.specs_by_model[model]['files'].append(specs)
                
                # Keep unique values for certain fields
                for field in ['pixel_size_um', 'bits_stored', 'rows', 'columns']:
                    if field in specs:
                        if field not in self.specs_by_model[model]:
                            self.specs_by_model[model][field] = set()
                        self.specs_by_model[model][field].add(specs[field])
        
        print(f"\nProcessed {self.file_count} DICOM files")
        if self.error_count > 0:
            print(f"Encountered {self.error_count} errors")
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary report of extracted specifications.
        
        Returns:
            Dictionary containing summary statistics by model
        """
        summary = {
            'total_files_processed': self.file_count,
            'total_errors': self.error_count,
            'vendor_filter': self.vendor_filter,
            'models': {}
        }
        
        for model, data in self.specs_by_model.items():
            files = data['files']
            model_summary = {
                'file_count': len(files),
                'sample_file': files[0]['source_file'] if files else None,
            }
            
            # Add unique values for key specifications
            for field in ['pixel_size_um', 'bits_stored', 'rows', 'columns']:
                if field in data:
                    values = sorted(data[field])
                    model_summary[field] = values
            
            # Extract common specifications from first file
            if files:
                first_file = files[0]
                for key in ['manufacturer', 'software_versions', 'photometric_interpretation',
                           'window_center', 'window_width', 'rescale_intercept', 'rescale_slope']:
                    if key in first_file:
                        model_summary[key] = first_file[key]
            
            summary['models'][model] = model_summary
        
        return summary
    
    def print_summary(self) -> None:
        """Print a formatted summary of extracted specifications."""
        summary = self.generate_summary()
        
        print("\n" + "="*80)
        print("DICOM TECHNICAL SPECIFICATIONS SUMMARY")
        print("="*80)
        print(f"\nTotal files processed: {summary['total_files_processed']}")
        if summary['vendor_filter']:
            print(f"Vendor filter: {summary['vendor_filter']}")
        print(f"\nModels found: {len(summary['models'])}")
        
        for model, data in summary['models'].items():
            print(f"\n{'-'*80}")
            print(f"Model: {model}")
            print(f"{'-'*80}")
            print(f"Files analyzed: {data['file_count']}")
            print(f"Sample file: {data.get('sample_file', 'N/A')}")
            
            if 'manufacturer' in data:
                print(f"\nManufacturer: {data['manufacturer']}")
            if 'software_versions' in data:
                print(f"Software Version: {data['software_versions']}")
            
            print("\n📐 Detector Specifications:")
            if 'pixel_size_um' in data:
                sizes = data['pixel_size_um']
                print(f"  Pixel Size: {', '.join(map(str, sizes))} μm")
            if 'bits_stored' in data:
                bits = data['bits_stored']
                print(f"  Bit Depth: {', '.join(map(str, bits))} bits")
            if 'rows' in data and 'columns' in data:
                matrices = [f"{c}×{r}" for r, c in zip(data['rows'], data['columns'])]
                print(f"  Matrix Size: {', '.join(matrices)} pixels")
            
            print("\n🖼️  VOI LUT (Windowing):")
            if 'window_center' in data:
                print(f"  Window Center: {data['window_center']}")
            if 'window_width' in data:
                print(f"  Window Width: {data['window_width']}")
            
            print("\n🔄 Modality LUT:")
            if 'rescale_intercept' in data:
                print(f"  Rescale Intercept: {data['rescale_intercept']}")
            if 'rescale_slope' in data:
                print(f"  Rescale Slope: {data['rescale_slope']}")
            
            if 'photometric_interpretation' in data:
                print(f"\n📊 Photometric: {data['photometric_interpretation']}")
    
    def save_to_file(self, output_path: Path, format: str = 'json') -> None:
        """
        Save extracted specifications to a file.
        
        Args:
            output_path: Path to output file
            format: Output format ('json' or 'markdown')
        """
        summary = self.generate_summary()
        
        if format == 'json':
            # Convert sets to lists for JSON serialization
            def convert_sets(obj):
                if isinstance(obj, set):
                    return sorted(list(obj))
                elif isinstance(obj, dict):
                    return {k: convert_sets(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_sets(i) for i in obj]
                return obj
            
            summary = convert_sets(summary)
            
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n✅ Saved JSON report to: {output_path}")
            
        elif format == 'markdown':
            with open(output_path, 'w') as f:
                f.write("# DICOM Technical Specifications Report\n\n")
                f.write(f"**Generated:** {Path.cwd()}\n")
                f.write(f"**Files Processed:** {summary['total_files_processed']}\n")
                if summary['vendor_filter']:
                    f.write(f"**Vendor Filter:** {summary['vendor_filter']}\n")
                f.write("\n---\n\n")
                
                for model, data in summary['models'].items():
                    f.write(f"## {model}\n\n")
                    f.write(f"**Files Analyzed:** {data['file_count']}\n\n")
                    
                    f.write("### Detector Specifications\n\n")
                    if 'pixel_size_um' in data:
                        f.write(f"- **Pixel Size:** {', '.join(map(str, sorted(data['pixel_size_um'])))} μm\n")
                    if 'bits_stored' in data:
                        f.write(f"- **Bit Depth:** {', '.join(map(str, sorted(data['bits_stored'])))} bits\n")
                    if 'rows' in data and 'columns' in data:
                        matrices = [f"{c}×{r}" for r, c in zip(sorted(data['rows']), sorted(data['columns']))]
                        f.write(f"- **Matrix Size:** {', '.join(matrices)} pixels\n")
                    
                    f.write("\n### VOI LUT Parameters\n\n")
                    if 'window_center' in data:
                        f.write(f"- **Window Center:** {data['window_center']}\n")
                    if 'window_width' in data:
                        f.write(f"- **Window Width:** {data['window_width']}\n")
                    
                    if 'rescale_intercept' in data or 'rescale_slope' in data:
                        f.write("\n### Modality LUT\n\n")
                        if 'rescale_intercept' in data:
                            f.write(f"- **Rescale Intercept:** {data['rescale_intercept']}\n")
                        if 'rescale_slope' in data:
                            f.write(f"- **Rescale Slope:** {data['rescale_slope']}\n")
                    
                    f.write("\n---\n\n")
            
            print(f"\n✅ Saved Markdown report to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract technical specifications from DICOM files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract specs from InBreast dataset (Siemens only)
  python extract_dicom_specs.py /path/to/InBreast --vendor Siemens
  
  # Extract from all vendors and save to JSON
  python extract_dicom_specs.py /path/to/dicoms --output specs.json
  
  # Extract and save as Markdown report
  python extract_dicom_specs.py /path/to/dicoms --output specs.md --format markdown
        """
    )
    
    parser.add_argument('directory', type=str, help='Directory containing DICOM files')
    parser.add_argument('--vendor', type=str, help='Filter by manufacturer (e.g., "Siemens")')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--no-recursive', action='store_true',
                       help='Do not search subdirectories')
    
    args = parser.parse_args()
    
    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)
    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        sys.exit(1)
    
    # Extract specifications
    extractor = DicomSpecsExtractor(vendor_filter=args.vendor)
    extractor.extract_from_directory(directory, recursive=not args.no_recursive)
    
    # Print summary
    extractor.print_summary()
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        extractor.save_to_file(output_path, format=args.format)
    
    print("\n" + "="*80)
    print("✅ Extraction complete!")
    print("="*80)


if __name__ == '__main__':
    main()
