"""
Shared fixtures for api_stable tests.
"""
import json
import numpy as np
import pytest
from pathlib import Path


# ---------------------------------------------------------------------------
# Raw pixel arrays
# ---------------------------------------------------------------------------

@pytest.fixture
def gray_uint8():
    """64x64 uint8 grayscale image with varied content."""
    rng = np.random.default_rng(42)
    return (rng.integers(30, 220, size=(64, 64))).astype(np.uint8)


@pytest.fixture
def gray_uint16():
    """64x64 uint16 image simulating a 12-bit DICOM range."""
    rng = np.random.default_rng(42)
    return (rng.integers(200, 3800, size=(64, 64))).astype(np.uint16)


@pytest.fixture
def monochrome1_uint8():
    """64x64 image whose bright areas appear dark (MONOCHROME1 convention)."""
    rng = np.random.default_rng(7)
    return (rng.integers(30, 220, size=(64, 64))).astype(np.uint8)


@pytest.fixture
def constant_uint8():
    """All-zero image: tests edge cases in normalization / windowing."""
    return np.zeros((32, 32), dtype=np.uint8)


# ---------------------------------------------------------------------------
# PNG files (tmp_path scoped per test)
# ---------------------------------------------------------------------------

@pytest.fixture
def png_gray_uint8(tmp_path, gray_uint8):
    """Write gray_uint8 to a PNG and return its Path."""
    import matplotlib.pyplot as plt
    path = tmp_path / "gray_uint8.png"
    plt.imsave(path, gray_uint8, cmap="gray")
    return path


@pytest.fixture
def png_constant(tmp_path, constant_uint8):
    """Write constant_uint8 to a PNG and return its Path."""
    import matplotlib.pyplot as plt
    path = tmp_path / "constant.png"
    plt.imsave(path, constant_uint8, cmap="gray")
    return path


# ---------------------------------------------------------------------------
# Metadata preset file
# ---------------------------------------------------------------------------

@pytest.fixture
def presets_path():
    """Return the bundled presets.json path."""
    return Path(__file__).parents[1] / "api_stable" / "metadata" / "presets.json"


@pytest.fixture
def custom_presets_file(tmp_path):
    """Write a one-entry preset JSON and return its Path."""
    data = {
        "TestVendor": {
            "vendor": {"manufacturer": "TEST_MANUFACTURER", "model_name": "TEST_MODEL"},
            "image": {"photometric_interpretation": "MONOCHROME2", "voi_lut_function": "LINEAR"},
        }
    }
    p = tmp_path / "custom_presets.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.fixture
def custom_defaults_file(tmp_path):
    """Write a flat defaults JSON (not a preset collection) and return its Path."""
    data = {
        "vendor": {"manufacturer": "FILE_VENDOR", "model_name": "FILE_MODEL"},
        "image": {"photometric_interpretation": "MONOCHROME1"},
    }
    p = tmp_path / "custom_defaults.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p
