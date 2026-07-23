try:
    from .extract_metadata import (
        extract_patient_info,
        extract_study_info,
        extract_manufacturer_info,
        extract_image_info,
        extract_acquisition_info,
        extract_compression_info,
        extract_metadata,
    )
except ImportError as e:
    print(f"Error importing metadata module: {e}")