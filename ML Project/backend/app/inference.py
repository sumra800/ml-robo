from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
import cv2
import numpy as np
from ultralytics import YOLO

from .bin_mapper import recommended_bin, robot_action
from .config import CONFIDENCE_THRESHOLD
from .model_manager import resolve_model_path


@dataclass
class InferenceStatus:
    ready: bool
    message: str


class WasteDetector:
    def __init__(self, conf_threshold=CONFIDENCE_THRESHOLD):
        self.model_path = None
        self.model_source = "unresolved"
        self.conf_threshold = conf_threshold
        self.model = None
        self.status = InferenceStatus(ready=False, message="Model not loaded")
        self._load_model()

    def _load_model(self) -> None:
        try:
            model_path, source, resolution_message = resolve_model_path()
            self.model_source = source
            self.model_path = model_path
            if model_path is None:
                self.status = InferenceStatus(ready=False, message=resolution_message)
                return
            self.model = YOLO(str(self.model_path))
            self.status = InferenceStatus(
                ready=True,
                message=f"{resolution_message} (loaded successfully)",
            )
        except Exception as exc:  # pragma: no cover
            self.status = InferenceStatus(ready=False, message=f"Failed to load model: {exc}")

    def detect_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Invalid image bytes")
        return self.detect_from_ndarray(image)

    def detect_from_ndarray(self, image: np.ndarray) -> Dict[str, Any]:
        if not self.status.ready or self.model is None:
            raise RuntimeError(self.status.message)

        height, width = image.shape[:2]
        results = self.model.predict(
            source=image,
            conf=self.conf_threshold,
            verbose=False,
        )
        detections: List[Dict[str, Any]] = []

        for result in results:
            names = result.names
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls_id = int(box.cls.item())
                class_name = names.get(cls_id, str(cls_id))
                confidence = float(box.conf.item())
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
                detections.append(
                    {
                        "class_name": class_name,
                        "confidence": round(confidence, 4),
                        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                        "recommended_bin": recommended_bin(class_name),
                        "action": robot_action(class_name),
                    }
                )

        return {
            "image_width": width,
            "image_height": height,
            "detections": detections,
        }


detector = WasteDetector()
