from __future__ import annotations

import os
from typing import Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from utils.yolox_interface import YOLOXNotebookInterface


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


YOLOX_ROOT = os.environ.get("YOLOX_ROOT", "/workspace/MyYoloX")
YOLOX_EXP_FILE = os.environ.get("YOLOX_EXP_FILE", "/workspace/MyYoloX/exps/default/yolox_nano.py")
YOLOX_CKPT = os.environ.get("YOLOX_CKPT", "/workspace/MyYoloX/archive/yolox_nano_416_roi_torch.pth")
YOLOX_DEVICE = os.environ.get("YOLOX_DEVICE", "cpu")
YOLOX_CONF = float(os.environ.get("YOLOX_CONF", "0.25"))
YOLOX_NMS = float(os.environ.get("YOLOX_NMS", "0.45"))
YOLOX_TSIZE = int(os.environ.get("YOLOX_TSIZE", "416"))
YOLOX_FP16 = _to_bool(os.environ.get("YOLOX_FP16", "0"))

app = FastAPI(title="YOLOX Inference API", version="0.1.0")

predictor: Optional[YOLOXNotebookInterface] = None


@app.on_event("startup")
def _startup() -> None:
    global predictor
    predictor = YOLOXNotebookInterface(
        exp_file=YOLOX_EXP_FILE,
        ckpt_path=YOLOX_CKPT,
        device=YOLOX_DEVICE,
        conf=YOLOX_CONF,
        nms=YOLOX_NMS,
        tsize=YOLOX_TSIZE,
        fp16=YOLOX_FP16,
        yolox_root=YOLOX_ROOT,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "yolox"}


@app.post("/infer")
async def infer(
    file: UploadFile = File(...),
    input_format: str = Form("BGR"),
    score_threshold: Optional[float] = Form(None),
) -> dict:
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not initialized")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty input file")

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise HTTPException(status_code=400, detail="Unable to decode image")

    detections = predictor.predict(
        image=image,
        input_format=input_format,
        score_threshold=score_threshold,
    )

    return {
        "num_detections": len(detections),
        "detections": detections,
        "image_shape": list(image.shape),
    }
