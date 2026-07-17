"""Notebook-friendly wrapper for MAseg pectoral muscle segmentation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import sys

import numpy as np


class MAsegPectoralSegmentationInterface:
    """Runs MAseg model inference on in-memory mammography images.

    Output labels are expected as:
    - 0: background
    - 1: breast region
    - 2: pectoral muscle
    """

    def __init__(
        self,
        weights_path: str,
        maseg_root: Optional[str] = None,
    ) -> None:
        self.maseg_root = self._resolve_maseg_root(maseg_root)
        self.weights_path = str(Path(weights_path).expanduser().resolve())

        if not Path(self.weights_path).exists():
            raise FileNotFoundError(f"weights file not found: {self.weights_path}")

        self._RunModel = self._bootstrap_run_model()
        self._model = self._RunModel(self.weights_path)

    @staticmethod
    def _resolve_maseg_root(maseg_root: Optional[str]) -> Path:
        if maseg_root:
            root = Path(maseg_root).expanduser().resolve()
        else:
            project_root = Path(__file__).resolve().parents[3]
            candidates = [
                project_root / "BreastSegmentationUnet" / "maseg",
                project_root / "common_tasks" / "segmentation" / "BreastSegmentationUnet" / "maseg",
            ]
            root = next((cand for cand in candidates if cand.exists()), candidates[0])

        if root.name != "maseg" and (root / "maseg").exists():
            root = root / "maseg"

        if not root.exists():
            raise FileNotFoundError(f"MAseg root not found: {root}")
        return root

    def _bootstrap_run_model(self):
        package_root = str(self.maseg_root.parent)
        if package_root not in sys.path:
            sys.path.insert(0, package_root)

        try:
            from maseg.run_model import RunModel  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as exc:
            missing = getattr(exc, "name", None) or "unknown"
            raise RuntimeError(
                "Unable to import MAseg RunModel because a dependency is missing "
                f"('{missing}'). Install MAseg dependencies in the active environment "
                "(at minimum: torch, pytorch_lightning, SimpleITK)."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "Unable to import MAseg RunModel. Ensure the MAseg package root is on sys.path "
                "and its dependencies are installed in the same environment as the notebook kernel."
            ) from exc

        return RunModel

    @staticmethod
    def _to_float32_image(image: Any) -> np.ndarray:
        arr = np.asarray(image)
        if arr.ndim == 3:
            # If RGB-like image is given, convert to grayscale by channel mean.
            arr = arr.mean(axis=2)
        if arr.ndim != 2:
            raise ValueError("image must be a 2D array or a 3-channel image")
        return arr.astype(np.float32)

    def segment(
        self,
        image: Any,
        fill_holes_in_breast: bool = True,
    ) -> np.ndarray:
        """Returns a segmentation mask with labels {0,1,2}."""

        image_2d = self._to_float32_image(image)
        mask = self._model.get_segmentation(
            image_2d,
            fill_holes_in_breast=fill_holes_in_breast,
            output_size=image_2d.shape,
        )
        return np.asarray(mask, dtype=np.uint8)

    @staticmethod
    def pectoral_mask(segmentation_mask: np.ndarray) -> np.ndarray:
        """Returns binary pectoral mask from a MAseg segmentation mask."""

        mask = np.asarray(segmentation_mask)
        return (mask == 2).astype(np.uint8)

    @staticmethod
    def summary(segmentation_mask: np.ndarray) -> Dict[str, int]:
        """Returns pixel counts for background, breast and pectoral classes."""

        mask = np.asarray(segmentation_mask)
        return {
            "background_pixels": int((mask == 0).sum()),
            "breast_pixels": int((mask == 1).sum()),
            "pectoral_pixels": int((mask == 2).sum()),
        }

    @staticmethod
    def overlay(
        image: Any,
        segmentation_mask: np.ndarray,
        alpha: float = 0.35,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Returns RGB overlays for breast and pectoral masks."""

        img = np.asarray(image)
        if img.ndim == 2:
            img = np.stack([img, img, img], axis=-1)
        elif img.ndim == 3 and img.shape[2] == 1:
            img = np.repeat(img, 3, axis=2)

        if img.ndim != 3 or img.shape[2] != 3:
            raise ValueError("image must be grayscale or RGB-like")

        img = img.astype(np.float32)
        min_v = float(img.min())
        max_v = float(img.max())
        if max_v > min_v:
            img = (img - min_v) / (max_v - min_v)
        img = (img * 255.0).clip(0, 255).astype(np.uint8)

        seg = np.asarray(segmentation_mask)
        breast = (seg == 1)
        pectoral = (seg == 2)

        breast_overlay = img.copy()
        pectoral_overlay = img.copy()

        breast_color = np.array([255, 165, 0], dtype=np.float32)  # orange
        pectoral_color = np.array([0, 220, 60], dtype=np.float32)  # green

        breast_overlay[breast] = (
            (1.0 - alpha) * breast_overlay[breast].astype(np.float32) + alpha * breast_color
        ).astype(np.uint8)

        pectoral_overlay[pectoral] = (
            (1.0 - alpha) * pectoral_overlay[pectoral].astype(np.float32) + alpha * pectoral_color
        ).astype(np.uint8)

        return breast_overlay, pectoral_overlay
