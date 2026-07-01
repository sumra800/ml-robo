from __future__ import annotations

import base64
import binascii
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .inference import detector
from .schemas import Base64Request, DetectResponse


app = FastAPI(title="Waste Sorting Vision API", version="1.0.0")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok" if detector.status.ready else "degraded",
        "model_ready": detector.status.ready,
        "message": detector.status.message,
        "model_source": detector.model_source,
        "model_path": str(detector.model_path) if detector.model_path else None,
    }


@app.post("/detect", response_model=DetectResponse)
async def detect(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        return detector.detect_from_bytes(image_bytes)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc


@app.post("/detect/base64", response_model=DetectResponse)
def detect_base64(payload: Base64Request):
    data = payload.image_base64.strip()
    if "," in data and data.lower().startswith("data:image"):
        data = data.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 payload") from exc

    try:
        return detector.detect_from_bytes(image_bytes)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc
