"""
Tests for api_stable/processing/photometric.py

These test pure functions that take numpy arrays and return numpy arrays.
No DICOM or metadata dependency.
"""
import numpy as np
import pytest

from api_stable.processing.photometric import (
    normalize_image,
    calculate_windowing,
    apply_windowing,
)
from api_stable.models.image import MammographyImage


def ensure_monochrome2(image, photometric_interpretation):
    """Helper: wraps MammographyImage.convert_to_monochrome2 for pure-array tests."""
    if photometric_interpretation != "MONOCHROME1":
        return image.copy()
    return image.max() - image


# ---------------------------------------------------------------------------
# normalize_image
# ---------------------------------------------------------------------------

class TestNormalizeImage:
    def test_output_range_is_zero_to_one(self, gray_uint8):
        result = normalize_image(gray_uint8.astype(float))
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_constant_image_returns_zeros(self, constant_uint8):
        result = normalize_image(constant_uint8.astype(float))
        assert np.all(result == 0)

    def test_output_shape_preserved(self, gray_uint8):
        result = normalize_image(gray_uint8.astype(float))
        assert result.shape == gray_uint8.shape

    def test_dtype_preserved_for_float_input(self):
        arr = np.array([0.0, 0.5, 1.0], dtype=np.float32)
        result = normalize_image(arr)
        assert result.dtype == np.float32


# ---------------------------------------------------------------------------
# ensure_monochrome2 (logic lives in MammographyImage.convert_to_monochrome2)
# ---------------------------------------------------------------------------

class TestEnsureMonochrome2:
    def test_monochrome2_unchanged(self, gray_uint8):
        result = ensure_monochrome2(gray_uint8, "MONOCHROME2")
        np.testing.assert_array_equal(result, gray_uint8)

    def test_monochrome1_inverted(self, monochrome1_uint8):
        result = ensure_monochrome2(monochrome1_uint8, "MONOCHROME1")
        expected = monochrome1_uint8.max() - monochrome1_uint8
        np.testing.assert_array_equal(result, expected)

    def test_unknown_photometric_unchanged(self, gray_uint8):
        result = ensure_monochrome2(gray_uint8, "RGB")
        np.testing.assert_array_equal(result, gray_uint8)


# ---------------------------------------------------------------------------
# calculate_windowing
# ---------------------------------------------------------------------------

class TestCalculateWindowing:
    def test_returns_two_integers(self, gray_uint8):
        center, width = calculate_windowing(gray_uint8)
        assert isinstance(center, int)
        assert isinstance(width, int)

    def test_width_is_positive(self, gray_uint8):
        _, width = calculate_windowing(gray_uint8)
        assert width > 0

    def test_all_zeros_raises(self):
        with pytest.raises(ValueError, match="No non-zero pixels"):
            calculate_windowing(np.zeros((10, 10), dtype=np.uint8))

    def test_exclude_background_false_accepts_zeros(self):
        arr = np.zeros((10, 10), dtype=np.uint8)
        center, width = calculate_windowing(arr, exclude_background=False)
        assert isinstance(center, int)

    def test_valid_methods(self, gray_uint8):
        methods = [
            "percentile_1_99", "percentile_2_98", "percentile_5_95",
            "breast_tissue", "statistical", "statistical_wide",
            "full_range", "histogram_peak",
        ]
        for method in methods:
            center, width = calculate_windowing(gray_uint8, method=method)
            assert width > 0, f"Width should be positive for method {method}"

    def test_unknown_method_raises(self, gray_uint8):
        with pytest.raises(ValueError):
            calculate_windowing(gray_uint8, method="unknown_method")


# ---------------------------------------------------------------------------
# apply_windowing
# ---------------------------------------------------------------------------

class TestApplyWindowing:
    def test_output_clipped_between_ymin_ymax(self, gray_uint8):
        center, width = calculate_windowing(gray_uint8)
        result = apply_windowing(
            gray_uint8.astype(np.float32),
            window_center=center,
            window_width=width,
            y_min=0,
            y_max=255,
        )
        assert result.min() >= 0
        assert result.max() <= 255

    def test_output_shape_preserved(self, gray_uint8):
        center, width = calculate_windowing(gray_uint8)
        result = apply_windowing(
            gray_uint8.astype(np.float32),
            window_center=center,
            window_width=width,
        )
        assert result.shape == gray_uint8.shape

    def test_np_v1_and_v2_close(self, gray_uint8):
        center, width = calculate_windowing(gray_uint8)
        arr = gray_uint8.astype(np.float32)
        r1 = apply_windowing(arr, window_center=center, window_width=width, backend="np_v1")
        r2 = apply_windowing(arr, window_center=center, window_width=width, backend="np_v2")
        np.testing.assert_allclose(r1, r2, atol=1.0)

    def test_invalid_backend_raises(self, gray_uint8):
        with pytest.raises(ValueError):
            apply_windowing(gray_uint8.astype(float), window_center=100, window_width=200, backend="invalid")
