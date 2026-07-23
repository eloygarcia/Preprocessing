"""
This module provides functions to extract metadata from DICOM datasets using the pydicom library. It includes functions to extract patient information, study information, manufacturer information, image information, acquisition information, and compression information from a DICOM dataset.
The extracted metadata is returned as dictionaries for easy access and further processing.
Functions:
- extract_patient_info(ds): Extracts patient information from a DICOM dataset.
- extract_study_info(ds): Extracts study information from a DICOM dataset.
- extract_manufacturer_info(ds): Extracts manufacturer information from a DICOM dataset.
- extract_image_info(ds): Extracts image information from a DICOM dataset.
- extract_acquisition_info(ds): Extracts acquisition information from a DICOM dataset.
- extract_compression_info(ds): Extracts compression information from a DICOM dataset.
"""

import pydicom

def extract_patient_info(ds):
    """
    Extracts patient information from a DICOM dataset.

    Parameters:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.

    Returns:
        dict: A dictionary containing patient information.
    """ 
    patient_info = {
        "PatientID": getattr(ds, "PatientID", None),
        "PatientName": getattr(ds, "PatientName", None),
        "PatientBirthDate": getattr(ds, "PatientBirthDate", None),
        "PatientSex": getattr(ds, "PatientSex", None),
        "PatientAge": getattr(ds, "PatientAge", None),
    }
    return patient_info

def extract_study_info(ds):
    """
    Extracts study information from a DICOM dataset.

    Parameters:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.
    Returns:
        dict: A dictionary containing study information.
    """
    study_info = {
        "StudyInstanceUID": getattr(ds, "StudyInstanceUID", None),
        "StudyDate": getattr(ds, "StudyDate", None),
        "StudyTime": getattr(ds, "StudyTime", None),
        "AccessionNumber": getattr(ds, "AccessionNumber", None),
        "ReferringPhysicianName": getattr(ds, "ReferringPhysicianName", None),
    }
    return study_info

def extract_manufacturer_info(ds):
    """
    Extracts manufacturer information from a DICOM dataset.

    Parameters:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.
    Returns:
        dict: A dictionary containing manufacturer information.
    """
    manufacturer_info = {
        "Manufacturer": getattr(ds, "Manufacturer", None),
        "ManufacturerModelName": getattr(ds, "ManufacturerModelName", None),
        "DeviceSerialNumber": getattr(ds, "DeviceSerialNumber", None),
    }
    return manufacturer_info

def extract_image_info(ds):
    """
    Extracts image information from a DICOM dataset.

    Parameters:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.
    Returns:
        dict: A dictionary containing image information.
    """
    image_info = {
        "Rows": getattr(ds, "Rows", None),
        "Columns": getattr(ds, "Columns", None),
        "PixelSpacing": getattr(ds, "PixelSpacing", None),
        "PixelImagerSpacing": getattr(ds, "PixelImagerSpacing", None),
        #"SliceThickness": getattr(ds, "SliceThickness", None),
        #"ImagePositionPatient": getattr(ds, "ImagePositionPatient", None),
        #"ImageOrientationPatient": getattr(ds, "ImageOrientationPatient", None),
    }
    return image_info

def extract_acquisition_info(ds):
    """
    Extracts acquisition information from a DICOM dataset.

    Parameters:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.
    Returns:
        dict: A dictionary containing acquisition information.
    """
    acquisition_info = {
        "Modality": getattr(ds, "Modality", None),
        "SeriesInstanceUID": getattr(ds, "SeriesInstanceUID", None),
        "SeriesNumber": getattr(ds, "SeriesNumber", None),
        "AcquisitionDateTime": getattr(ds, "AcquisitionDateTime", None),
        "AcquisitionNumber": getattr(ds, "AcquisitionNumber", None),
    }
    return acquisition_info 


def extract_compression_info(ds):
    """
    Extracts compression information from a DICOM dataset.

    Parameters:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.
    Returns:
        dict: A dictionary containing compression information.
    """ 
    compression_info = {
        "CompressionForceNewtons": getattr(ds, "CompressionForceNewtons", None),
    }
    return compression_info


def extract_metadata(ds):
    """
    Extracts all relevant metadata from a DICOM dataset.

    Parameters:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.
    Returns:
        dict: A dictionary containing all extracted metadata.
    """
    metadata = {
        "PatientInfo": extract_patient_info(ds),
        "StudyInfo": extract_study_info(ds),
        "ManufacturerInfo": extract_manufacturer_info(ds),
        "ImageInfo": extract_image_info(ds),
        "AcquisitionInfo": extract_acquisition_info(ds),
        "CompressionInfo": extract_compression_info(ds),
    }
    return metadata
