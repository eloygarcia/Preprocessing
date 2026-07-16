"""
Tests for api_stable/models/image.py

MammographyImage must remain pixel-only: no DICOM dataset access,
all transformation parameters must be explicit.
"""
import numpy as np
import pytest

from api_stable.models.image import MammographyImage


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestMammographyImageConstruction:
    def test_shape(self, gray_uint8):
        img = MammographyImage(gray_uint8)
        assert img.shape == gray_uint8.shape

    def test_dtype(self, gray_uint8):
        img = MammographyImage(gray_uint8)
        assert img.dtype == gray_uint8.dtype

    def test_min_max(self, gray_uint8):
        img = MammographyImage(gray_uint8)
        assert img.min == gray_uint8.min()
        assert img.max == gray_uint8.max()

    def test_history_starts_empty(self, gray_uint8):
        img = MammographyImage(gray_uint8)
        assert img.get_history() == []

    def test_last_windowing_starts_none(self, gray_uint8):
        img = MammographyImage(gray_uint8)
        assert img.last_windowing is None

    def test_no_ds_dependency(self, gray_uint8):
        """Constructor must not accept ds; passing one would be a regression."""
        import inspect
        sig = inspect.signature(MammographyImage.__init__)
        assert "ds" not in sig.parameters


# ---------------------------------------------------------------------------
# copy / to_numpy
# ---------------------------------------------------------------------------

class TestMammographyImageCopy:
    def test_copy_is_independent(self, gray_uint8):
        img = MammographyImage(gray_uint8.copy())
        copy = img.copy()
        copy.normalize()
        # original must be unchanged
        assert img.get_history() == []

    def test_to_numpy_returns_array(self, gray_uint8):
        img = MammographyImage(gray_uint8)
        assert isinstance(img.to_numpy(), np.ndarray)


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_normalize_appends_history(self, gray_uint8):
        img = MammographyImage(gray_uint8.astype(float))
        img.normalize()
        assert "normalize" in img.get_history()

    def test_normalize_returns_self(self, gray_uint8):
        img = MammographyImage(gray_uint8.astype(float))
        result = img.normalize()
        assert result is img

    def test_normalize_constant_image_no_crash(self, constant_uint8):
        img = MammographyImage(constant_uint8.astype(float))
        img.normalize()  # must not raise


# ---------------------------------------------------------------------------
# convert_to_monochrome2
# ---------------------------------------------------------------------------

class TestConvertToMonochrome2:
    def test_inversion_correct(self, monochrome1_uint8):
        original = monochrome1_uint8.copy()
        img = MammographyImage(monochrome1_uint8.copy())
        img.convert_to_monochrome2()
        expected = original.max() - original
        np.testing.assert_array_equal(img.to_numpy(), expected)

    def test_history_updated(self, monochrome1_uint8):
        img = MammographyImage(monochrome1_uint8.copy())
        img.convert_to_monochrome2()
        assert "convert_to_monochrome2" in img.get_history()

    def test_returns_self(self, monochrome1_uint8):
        img = MammographyImage(monochrome1_uint8.copy())
        assert img.convert_to_monochrome2() is img


# ---------------------------------------------------------------------------
# apply_windowing
# ---------------------------------------------------------------------------

class TestApplyWindowing:
    def test_last_windowing_populated(self, gray_uint8):
        img = MammographyImage(gray_uint8.astype(float))
        img.apply_windowing(window_center=100, window_width=200)
        assert img.last_windowing is not None
        assert "window_center" in img.last_windowing
        assert "window_width" in img.last_windowing

    def test_history_contains_windowing_entry(self, gray_uint8):
        img = MammographyImage(gray_uint8.astype(float))
        img.apply_windowing(window_center=100, window_width=200)
        assert any("apply_windowing" in h for h in img.get_history())

    def test_no_params_falls_back_to_auto(self, gray_uint8):
        img = MammographyImage(gray_uint8.astype(float))
        img.apply_windowing()  # must not raise

    def test_returns_self(self, gray_uint8):
        img = MammographyImage(gray_uint8.astype(float))
        assert img.apply_windowing(window_center=100, window_width=200) is img


# ---------------------------------------------------------------------------
# chained operations
# ---------------------------------------------------------------------------

class TestChaining:
    def test_full_chain_history(self, gray_uint8):
        img = MammographyImage(gray_uint8.astype(float))
        img.convert_to_monochrome2().apply_windowing().normalize()
        history = img.get_history()
        assert len(history) == 3
        assert any("convert_to_monochrome2" in h for h in history)
        assert any("apply_windowing" in h for h in history)
        assert "normalize" in history
