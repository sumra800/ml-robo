from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import urlparse
from typing import Optional, Tuple

from .config import (
    MODEL_PATH,
    MODEL_URL,
    BOOTSTRAP_MODEL,
    DOWNLOADS_DIR,
    RUNS_DIR,
)


@dataclass
class ModelResolution:
    path: Optional[Path]
    source: str
    message: str


def _latest_checkpoint_from_runs() -> Optional[Path]:
    if not RUNS_DIR.exists():
        return None
    candidates = sorted(RUNS_DIR.glob("**/weights/best.pt"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def _download_model(url: str, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(urlparse(url).path).name or "downloaded_best.pt"
    target_path = target_dir / filename
    urlretrieve(url, target_path)
    return target_path


def _bootstrap_model(target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    # This path can be consumed by YOLO directly; YOLO will download if missing.
    return target_dir / BOOTSTRAP_MODEL


def resolve_model_path() -> Tuple[Optional[Path], str, str]:
    if MODEL_PATH.exists():
        return MODEL_PATH, "configured", f"Using configured model: {MODEL_PATH}"

    latest = _latest_checkpoint_from_runs()
    if latest and latest.exists():
        return latest, "latest-checkpoint", f"Using latest training checkpoint: {latest}"

    if MODEL_URL:
        try:
            downloaded = _download_model(MODEL_URL, DOWNLOADS_DIR)
            return downloaded, "downloaded", f"Downloaded model from URL to: {downloaded}"
        except Exception as exc:  # pragma: no cover
            bootstrap = _bootstrap_model(DOWNLOADS_DIR)
            return (
                bootstrap,
                "download-failed-bootstrap",
                f"Model URL download failed ({exc}). Falling back to bootstrap model: {bootstrap}",
            )

    bootstrap = _bootstrap_model(DOWNLOADS_DIR)
    return bootstrap, "bootstrap", f"Using bootstrap model: {bootstrap}"
