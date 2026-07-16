"""
Tests for api_stable/mammography.py  (MammographyDicom)

Covers constructors (from_numpy / from_png), metadata preset wiring,
pipeline orchestration (initialize_image, normalize), and metadata sync
after transformations.
"""
import numpy as np
import pytest

from api_stable.mammography import MammographyDicom
from api_stable.models.metadata import MammographyMetadata


# ---------------------------------------------------------------------------
# from_numpy — array input
# ---------------------------------------------------------------------------

class TestFromNumpyArray:
    def test_image_shape(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        assert m.image.shape == gray_uint8.shape

    def test_metadata_created_by_default(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        assert m.metadata is not None
        assert isinstance(m.metadata, MammographyMetadata)

    def test_rows_columns_in_metadata(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        assert m.metadata.image.rows == gray_uint8.shape[0]
        assert m.metadata.image.columns == gray_uint8.shape[1]

    def test_metadata_preset_applied(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8, metadata_preset="Hologic")
        assert m.metadata.vendor.manufacturer == "HOLOGIC, Inc."

    def test_metadata_defaults_applied(self, gray_uint8):
        m = MammographyDicom.from_numpy(
            gray_uint8,
            metadata_defaults={"vendor": {"manufacturer": "ACME", "model_name": None}},
        )
        assert m.metadata.vendor.manufacturer == "ACME"

    def test_metadata_overrides_applied(self, gray_uint8):
        m = MammographyDicom.from_numpy(
            gray_uint8,
            metadata_preset="Hologic",
            metadata_overrides={"breast": {"laterality": "R", "view": "CC"}},
        )
        assert m.metadata.breast.laterality == "R"
        assert m.metadata.vendor.manufacturer == "HOLOGIC, Inc."

    def test_explicit_metadata_wins_over_preset(self, gray_uint8):
        from api_stable.metadata.factory import MetadataFactory
        custom_md = MetadataFactory.create_preset("Siemens", pixel_array=gray_uint8)
        m = MammographyDicom.from_numpy(gray_uint8, metadata=custom_md)
        assert m.metadata.vendor.manufacturer == "Siemens"


# ---------------------------------------------------------------------------
# from_numpy — PNG path input
# ---------------------------------------------------------------------------

class TestFromNumpyPNGPath:
    def test_from_numpy_with_png_path(self, png_gray_uint8):
        m = MammographyDicom.from_numpy(png_gray_uint8)
        assert m.image.shape[0] > 0
        assert m.metadata is not None

    def test_path_stored(self, png_gray_uint8):
        m = MammographyDicom.from_numpy(png_gray_uint8)
        assert m.path == png_gray_uint8


# ---------------------------------------------------------------------------
# from_png
# ---------------------------------------------------------------------------

class TestFromPNG:
    def test_basic_load(self, png_gray_uint8):
        m = MammographyDicom.from_png(png_gray_uint8)
        assert m.image.shape[0] > 0

    def test_metadata_created(self, png_gray_uint8):
        m = MammographyDicom.from_png(png_gray_uint8)
        assert isinstance(m.metadata, MammographyMetadata)

    def test_preset_applied(self, png_gray_uint8):
        m = MammographyDicom.from_png(png_gray_uint8, metadata_preset="GE")
        assert m.metadata.vendor.manufacturer == "GE Healthcare"
        assert m.metadata.image.voi_lut_function == "SIGMOID"

    def test_overrides_applied_on_top_of_preset(self, png_gray_uint8):
        m = MammographyDicom.from_png(
            png_gray_uint8,
            metadata_preset="Hologic",
            metadata_overrides={"breast": {"laterality": "L", "view": "MLO"}},
        )
        assert m.metadata.breast.laterality == "L"
        assert m.metadata.vendor.manufacturer == "HOLOGIC, Inc."

    def test_constant_png_no_crash(self, png_constant):
        m = MammographyDicom.from_png(png_constant)
        assert m.image is not None


# ---------------------------------------------------------------------------
# initialize_image (MONOCHROME1 -> MONOCHROME2 + windowing)
# ---------------------------------------------------------------------------

class TestInitializeImage:
    def test_monochrome1_converted_to_monochrome2(self, gray_uint8):
        m = MammographyDicom.from_numpy(
            gray_uint8,
            metadata_overrides={"image": {"photometric_interpretation": "MONOCHROME1"}},
        )
        m.initialize_image()
        assert m.metadata.image.photometric_interpretation == "MONOCHROME2"

    def test_monochrome2_not_converted(self, gray_uint8):
        original = gray_uint8.copy()
        m = MammographyDicom.from_numpy(gray_uint8)
        assert m.metadata.image.photometric_interpretation == "MONOCHROME2"
        m.initialize_image()
        assert "convert_to_monochrome2" not in m.image.get_history()

    def test_windowing_recorded_in_history(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        m.initialize_image()
        assert any("apply_windowing" in h for h in m.image.get_history())

    def test_windowing_explanation_updated_in_metadata(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        m.initialize_image()
        assert m.metadata.image.window_center_width_explanation == "APPLIED"

    def test_returns_self_for_chaining(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        assert m.initialize_image() is m


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_explanation_set_to_normalized(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        m.initialize_image().normalize()
        assert m.metadata.image.window_center_width_explanation == "NORMALIZED"

    def test_normalize_in_history(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        m.normalize()
        assert "normalize" in m.image.get_history()

    def test_returns_self_for_chaining(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        assert m.normalize() is m


# ---------------------------------------------------------------------------
# metadata sync after transformations
# ---------------------------------------------------------------------------

class TestMetadataSync:
    def test_rows_columns_stable_after_pipeline(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8)
        rows_before = m.metadata.image.rows
        m.initialize_image().normalize()
        assert m.metadata.image.rows == rows_before

    def test_vendor_preserved_after_pipeline(self, png_gray_uint8):
        import warnings
        m = MammographyDicom.from_png(png_gray_uint8, metadata_preset="Hologic")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            m.initialize_image().normalize()
        assert m.metadata.vendor.manufacturer == "HOLOGIC, Inc."

    def test_breast_overrides_preserved_after_pipeline(self, gray_uint8):
        m = MammographyDicom.from_numpy(
            gray_uint8,
            metadata_preset="GE",
            metadata_overrides={"breast": {"laterality": "R", "view": "CC"}},
        )
        m.initialize_image().normalize()
        assert m.metadata.breast.laterality == "R"
        assert m.metadata.breast.view == "CC"


# ---------------------------------------------------------------------------
# copy
# ---------------------------------------------------------------------------

class TestCopy:
    def test_copy_is_independent(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8.copy())
        c = m.copy()
        c.normalize()
        assert m.image.get_history() == []

    def test_copy_preserves_metadata(self, gray_uint8):
        m = MammographyDicom.from_numpy(gray_uint8, metadata_preset="Siemens")
        c = m.copy()
        assert c.metadata.vendor.manufacturer == "Siemens"
