from pydantic import BaseModel, Field
from typing import List


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_name: str = Field(description="Detected class label")
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox
    recommended_bin: str
    action: str


class DetectResponse(BaseModel):
    image_width: int
    image_height: int
    detections: List[Detection]


class Base64Request(BaseModel):
    image_base64: str
