"""
Tests for api_stable/metadata/factory.py

Covers: DICOM-less metadata creation from preset, dict, file,
deep-merge behaviour, and image metadata refresh after transformations.
"""
import numpy as np
import pytest

from api_stable.metadata.factory import MetadataFactory
from api_stable.models.metadata import (
    MammographyMetadata,
    PatientInfo,
    VendorInfo,
    AcquisitionInfo,
    BreastInfo,
    ImageInfo,
)


# ---------------------------------------------------------------------------
# create_default
# ---------------------------------------------------------------------------

class TestCreateDefault:
    def test_returns_metadata_instance(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        assert isinstance(md, MammographyMetadata)

    def test_rows_columns_from_array(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        assert md.image.rows == gray_uint8.shape[0]
        assert md.image.columns == gray_uint8.shape[1]

    def test_bits_stored_from_dtype(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        assert md.image.bits_stored == 8

    def test_bits_stored_uint16(self, gray_uint16):
        md = MetadataFactory.create_default(pixel_array=gray_uint16)
        assert md.image.bits_stored == 16

    def test_default_photometric_is_monochrome2(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        assert md.image.photometric_interpretation == "MONOCHROME2"

    def test_window_center_computed(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        assert md.image.window_center is not None

    def test_no_array_gives_none_rows(self):
        md = MetadataFactory.create_default()
        assert md.image.rows is None
        assert md.image.columns is None


# ---------------------------------------------------------------------------
# create_from_dict
# ---------------------------------------------------------------------------

class TestCreateFromDict:
    def test_vendor_override(self, gray_uint8):
        md = MetadataFactory.create_from_dict(
            {"vendor": {"manufacturer": "MY_VENDOR", "model_name": "MY_MODEL"}},
            pixel_array=gray_uint8,
        )
        assert md.vendor.manufacturer == "MY_VENDOR"

    def test_image_override_photometric(self, gray_uint8):
        md = MetadataFactory.create_from_dict(
            {"image": {"photometric_interpretation": "MONOCHROME1"}},
            pixel_array=gray_uint8,
        )
        assert md.image.photometric_interpretation == "MONOCHROME1"

    def test_unmentioned_fields_keep_defaults(self, gray_uint8):
        md = MetadataFactory.create_from_dict(
            {"vendor": {"manufacturer": "X", "model_name": None}},
            pixel_array=gray_uint8,
        )
        assert md.image.rows == gray_uint8.shape[0]
        assert md.patient.patient_id is None


# ---------------------------------------------------------------------------
# create_preset
# ---------------------------------------------------------------------------

class TestCreatePreset:
    def test_hologic_preset_vendor(self, gray_uint8, presets_path):
        md = MetadataFactory.create_preset("Hologic", pixel_array=gray_uint8)
        assert md.vendor.manufacturer == "HOLOGIC, Inc."
        assert md.vendor.model_name == "Selenia Dimensions"

    def test_ge_preset_voi_func(self, gray_uint8):
        md = MetadataFactory.create_preset("GE", pixel_array=gray_uint8)
        assert md.image.voi_lut_function == "SIGMOID"

    def test_siemens_preset(self, gray_uint8):
        md = MetadataFactory.create_preset("Siemens", pixel_array=gray_uint8)
        assert md.vendor.manufacturer == "Siemens"

    def test_case_insensitive(self, gray_uint8):
        md = MetadataFactory.create_preset("hologic", pixel_array=gray_uint8)
        assert md.vendor.manufacturer == "HOLOGIC, Inc."

    def test_unknown_preset_raises(self, gray_uint8):
        with pytest.raises(KeyError, match="Unknown metadata preset"):
            MetadataFactory.create_preset("UNKNOWN_VENDOR", pixel_array=gray_uint8)

    def test_custom_preset_from_dict(self, gray_uint8):
        custom = {
            "TestVendor": {
                "vendor": {"manufacturer": "TEST_MFR", "model_name": "TEST_MDL"},
                "image": {"voi_lut_function": "LINEAR"},
            }
        }
        md = MetadataFactory.create_preset("TestVendor", pixel_array=gray_uint8, presets=custom)
        assert md.vendor.manufacturer == "TEST_MFR"

    def test_override_merged_on_top_of_preset(self, gray_uint8):
        md = MetadataFactory.create_preset(
            "Hologic",
            pixel_array=gray_uint8,
            overrides={"breast": {"laterality": "L", "view": "MLO"}},
        )
        assert md.breast.laterality == "L"
        assert md.vendor.manufacturer == "HOLOGIC, Inc."

    def test_rows_columns_from_array(self, gray_uint8):
        md = MetadataFactory.create_preset("Hologic", pixel_array=gray_uint8)
        assert md.image.rows == gray_uint8.shape[0]


# ---------------------------------------------------------------------------
# create_from_file
# ---------------------------------------------------------------------------

class TestCreateFromFile:
    def test_flat_defaults_file(self, gray_uint8, custom_defaults_file):
        md = MetadataFactory.create_from_file(custom_defaults_file, pixel_array=gray_uint8)
        assert md.vendor.manufacturer == "FILE_VENDOR"
        assert md.image.photometric_interpretation == "MONOCHROME1"

    def test_preset_collection_without_name_raises(self, gray_uint8, custom_presets_file):
        with pytest.raises(ValueError, match="preset collection"):
            MetadataFactory.create_from_file(custom_presets_file, pixel_array=gray_uint8)

    def test_preset_collection_with_name(self, gray_uint8, custom_presets_file):
        md = MetadataFactory.create_from_file(
            custom_presets_file,
            pixel_array=gray_uint8,
            preset_name="TestVendor",
        )
        assert md.vendor.manufacturer == "TEST_MANUFACTURER"


# ---------------------------------------------------------------------------
# refresh_image_metadata
# ---------------------------------------------------------------------------

class TestRefreshImageMetadata:
    def test_rows_columns_updated(self, gray_uint8):
        small = np.zeros((10, 20), dtype=np.uint8)
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        refreshed = MetadataFactory.refresh_image_metadata(md, small)
        assert refreshed.image.rows == 10
        assert refreshed.image.columns == 20

    def test_vendor_preserved_after_refresh(self, gray_uint8):
        md = MetadataFactory.create_preset("Hologic", pixel_array=gray_uint8)
        updated = np.zeros((8, 8), dtype=np.uint8)
        refreshed = MetadataFactory.refresh_image_metadata(md, updated)
        assert refreshed.vendor.manufacturer == "HOLOGIC, Inc."

    def test_image_override_applied(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        refreshed = MetadataFactory.refresh_image_metadata(
            md, gray_uint8,
            image_overrides={"photometric_interpretation": "MONOCHROME2", "window_center_width_explanation": "APPLIED"},
        )
        assert refreshed.image.window_center_width_explanation == "APPLIED"


# ---------------------------------------------------------------------------
# to_dict
# ---------------------------------------------------------------------------

class TestToDict:
    def test_returns_dict(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        d = MetadataFactory.to_dict(md)
        assert isinstance(d, dict)
        assert "patient" in d
        assert "vendor" in d
        assert "image" in d

    def test_roundtrip(self, gray_uint8):
        md = MetadataFactory.create_default(pixel_array=gray_uint8)
        d = MetadataFactory.to_dict(md)
        md2 = MetadataFactory.create_from_dict(d, pixel_array=gray_uint8)
        assert md2.vendor.manufacturer == md.vendor.manufacturer
