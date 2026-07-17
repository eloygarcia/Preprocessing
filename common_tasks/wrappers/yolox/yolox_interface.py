"""Notebook-friendly interface for running YOLOX inference from in-memory images."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import sys


class YOLOXNotebookInterface:
    """Wraps MyYoloX inference to return bounding boxes from numpy images.

    Expected workflow:
    1) Build/run the project Docker image.
    2) Install MyYoloX package in editable mode inside that environment.
    3) Import this class in notebooks and call predict() with an image array.
    """

    def __init__(
        self,
        exp_file: str,
        ckpt_path: str,
        device: str = "cpu",
        conf: float = 0.25,
        nms: float = 0.45,
        tsize: int = 416,
        fp16: bool = False,
        fuse: bool = False,
        legacy: bool = False,
        class_names: Optional[Sequence[str]] = None,
        yolox_root: Optional[str] = None,
    ) -> None:
        self._cv2 = None
        self._np = None
        self._torch = None
        self._postprocess = None
        self._fuse_model = None
        self._preproc = None

        self.device = device.lower()
        if self.device not in {"cpu", "gpu"}:
            raise ValueError("device must be 'cpu' or 'gpu'")

        self.fp16 = fp16
        self.yolox_root = self._resolve_yolox_root(yolox_root)
        self.exp_file = str(Path(exp_file).expanduser().resolve())
        self.ckpt_path = str(Path(ckpt_path).expanduser().resolve())

        if not Path(self.exp_file).exists():
            raise FileNotFoundError(f"exp_file not found: {self.exp_file}")
        if not Path(self.ckpt_path).exists():
            raise FileNotFoundError(f"ckpt_path not found: {self.ckpt_path}")

        self._bootstrap_dependencies(legacy=legacy)

        exp = self._get_exp(self.exp_file, None)
        exp.test_conf = conf
        exp.nmsthre = nms
        exp.test_size = (tsize, tsize)

        model = exp.get_model()
        model.eval()

        if self.device == "gpu":
            if not self._torch.cuda.is_available():
                raise RuntimeError("device='gpu' but CUDA is not available")
            model.cuda()
            if self.fp16:
                model.half()

        ckpt = self._torch.load(self.ckpt_path, map_location="cpu", weights_only=False)
        state_dict = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
        model.load_state_dict(state_dict, strict=False)

        if fuse:
            model = self._fuse_model(model)

        self.model = model
        self.num_classes = exp.num_classes
        self.confthre = exp.test_conf
        self.nmsthre = exp.nmsthre
        self.test_size = exp.test_size

        if class_names is not None:
            self.class_names = list(class_names)
        else:
            self.class_names = list(self._COCO_CLASSES)

    @staticmethod
    def _resolve_yolox_root(yolox_root: Optional[str]) -> Path:
        if yolox_root:
            root = Path(yolox_root).expanduser().resolve()
        else:
            root = (Path(__file__).resolve().parent.parent / "MyYoloX").resolve()
        if not root.exists():
            raise FileNotFoundError(f"MyYoloX root not found: {root}")
        return root

    def _bootstrap_dependencies(self, legacy: bool) -> None:
        yolox_root_str = str(self.yolox_root)
        if yolox_root_str not in sys.path:
            sys.path.insert(0, yolox_root_str)

        try:
            import cv2  # pylint: disable=import-outside-toplevel
            import numpy as np  # pylint: disable=import-outside-toplevel
            import torch  # pylint: disable=import-outside-toplevel
            from yolox.data.data_augment import ValTransform  # pylint: disable=import-outside-toplevel
            from yolox.data.datasets import COCO_CLASSES  # pylint: disable=import-outside-toplevel
            from yolox.exp import get_exp  # pylint: disable=import-outside-toplevel
            from yolox.utils import fuse_model, postprocess  # pylint: disable=import-outside-toplevel
        except Exception as exc:
            raise RuntimeError(
                "Unable to import YOLOX runtime dependencies. "
                "Install MyYoloX requirements and run `pip install -e /workspace/MyYoloX` "
                "inside your Docker/container environment."
            ) from exc

        self._cv2 = cv2
        self._np = np
        self._torch = torch
        self._ValTransform = ValTransform
        self._COCO_CLASSES = COCO_CLASSES
        self._get_exp = get_exp
        self._fuse_model = fuse_model
        self._postprocess = postprocess
        self._preproc = ValTransform(legacy=legacy)

    def _to_uint8(self, img: Any) -> Any:
        arr = self._np.asarray(img)
        if arr.dtype == self._np.uint8:
            return arr

        arr = arr.astype("float32")
        min_val = float(arr.min())
        max_val = float(arr.max())
        if max_val <= min_val:
            return self._np.zeros_like(arr, dtype=self._np.uint8)

        arr = (arr - min_val) / (max_val - min_val)
        arr = (arr * 255.0).clip(0, 255).astype(self._np.uint8)
        return arr

    def _prepare_image(self, image: Any, input_format: str) -> Any:
        img = self._to_uint8(image)

        if img.ndim == 2:
            return self._cv2.cvtColor(img, self._cv2.COLOR_GRAY2BGR)

        if img.ndim != 3:
            raise ValueError("image must be 2D or 3D array")

        if img.shape[2] == 1:
            return self._cv2.cvtColor(img, self._cv2.COLOR_GRAY2BGR)

        fmt = input_format.upper()
        if img.shape[2] == 4:
            if fmt in {"RGBA", "RGB"}:
                return self._cv2.cvtColor(img, self._cv2.COLOR_RGBA2BGR)
            return self._cv2.cvtColor(img, self._cv2.COLOR_BGRA2BGR)

        if img.shape[2] != 3:
            raise ValueError("image with 3D shape must have 1, 3 or 4 channels")

        if fmt == "RGB":
            return self._cv2.cvtColor(img, self._cv2.COLOR_RGB2BGR)
        if fmt == "BGR":
            return img
        raise ValueError("input_format must be 'RGB' or 'BGR'")

    def predict(
        self,
        image: Any,
        input_format: str = "RGB",
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Run inference and return detections.

        Returns a list with dicts containing:
        - bbox_xyxy: [x1, y1, x2, y2]
        - score: objectness * class confidence
        - class_id
        - class_name
        """

        raw_bgr = self._prepare_image(image, input_format=input_format)
        h, w = raw_bgr.shape[:2]

        ratio = min(self.test_size[0] / h, self.test_size[1] / w)
        proc_img, _ = self._preproc(raw_bgr, None, self.test_size)

        tensor = self._torch.from_numpy(proc_img).unsqueeze(0).float()
        if self.device == "gpu":
            tensor = tensor.cuda()
            if self.fp16:
                tensor = tensor.half()

        with self._torch.no_grad():
            outputs = self.model(tensor)
            outputs = self._postprocess(
                outputs,
                self.num_classes,
                self.confthre,
                self.nmsthre,
                class_agnostic=True,
            )

        output = outputs[0]
        if output is None:
            return []

        output = output.cpu().numpy()
        output[:, 0:4] = output[:, 0:4] / ratio

        detections: List[Dict[str, Any]] = []
        for row in output:
            score = float(row[4] * row[5])
            if score_threshold is not None and score < score_threshold:
                continue

            x1, y1, x2, y2 = [float(v) for v in row[:4]]
            x1 = max(0.0, min(x1, float(w - 1)))
            x2 = max(0.0, min(x2, float(w - 1)))
            y1 = max(0.0, min(y1, float(h - 1)))
            y2 = max(0.0, min(y2, float(h - 1)))

            class_id = int(row[6])
            class_name = (
                self.class_names[class_id]
                if 0 <= class_id < len(self.class_names)
                else str(class_id)
            )

            detections.append(
                {
                    "bbox_xyxy": [x1, y1, x2, y2],
                    "score": score,
                    "class_id": class_id,
                    "class_name": class_name,
                }
            )

        return detections

    def predict_with_image(
        self,
        image: Any,
        input_format: str = "RGB",
        score_threshold: Optional[float] = None,
    ) -> Tuple[List[Dict[str, Any]], Any]:
        """Run predict and also return a RGB visualization image."""

        detections = self.predict(
            image=image,
            input_format=input_format,
            score_threshold=score_threshold,
        )

        vis_bgr = self._prepare_image(image, input_format=input_format).copy()
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["bbox_xyxy"]]
            label = f"{det['class_name']}:{det['score']:.3f}"
            self._cv2.rectangle(vis_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
            self._cv2.putText(
                vis_bgr,
                label,
                (x1, max(0, y1 - 8)),
                self._cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                self._cv2.LINE_AA,
            )

        vis_rgb = self._cv2.cvtColor(vis_bgr, self._cv2.COLOR_BGR2RGB)
        return detections, vis_rgb
