from __future__ import annotations

import base64
import os
from typing import Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from common_tasks.wrappers.segmentation import MAsegPectoralSegmentationInterface

def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


MASEG_ROOT = os.environ.get(
    "MASEG_ROOT",
    "/workspace/BreastSegmentationUnet/maseg",
)
MASEG_WEIGHTS = os.environ.get(
    "MASEG_WEIGHTS",
    "/workspace/BreastSegmentationUnet/maseg/weights/segmentation_weights.ckpt",
)

app = FastAPI(title="MAseg Inference API", version="0.1.0")

segmenter: Optional[MAsegPectoralSegmentationInterface] = None


@app.on_event("startup")
def _startup() -> None:
    global segmenter
    segmenter = MAsegPectoralSegmentationInterface(
        weights_path=MASEG_WEIGHTS,
        maseg_root=MASEG_ROOT,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "maseg"}


@app.post("/infer")
async def infer(
    file: UploadFile = File(...),
    include_pectoral_mask: bool = Form(False),
    fill_holes_in_breast: bool = Form(True),
) -> dict:
    if segmenter is None:
        raise HTTPException(status_code=503, detail="Model not initialized")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty input file")

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise HTTPException(status_code=400, detail="Unable to decode image")

    segmentation = segmenter.segment(image, fill_holes_in_breast=fill_holes_in_breast)
    stats = segmenter.summary(segmentation)

    response = {
        "image_shape": list(image.shape),
        "segmentation_shape": list(segmentation.shape),
        "summary": stats,
    }

    if include_pectoral_mask:
        pectoral = segmenter.pectoral_mask(segmentation).astype(np.uint8) * 255
        ok, encoded = cv2.imencode(".png", pectoral)
        if not ok:
            raise HTTPException(status_code=500, detail="Unable to encode pectoral mask")
        response["pectoral_mask_png_base64"] = base64.b64encode(encoded.tobytes()).decode("utf-8")

    return response
