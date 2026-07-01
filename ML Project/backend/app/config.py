from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"
MODELS_DIR = PROJECT_ROOT / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
DOWNLOADS_DIR = MODELS_DIR / "downloads"
RUNS_DIR = PROJECT_ROOT / "runs" / "waste"

MODEL_PATH = Path(os.getenv("WASTE_MODEL_PATH", str(DEFAULT_MODEL_PATH)))
CONFIDENCE_THRESHOLD = float(os.getenv("WASTE_CONF_THRESHOLD", "0.25"))
MODEL_URL = os.getenv("WASTE_MODEL_URL", "").strip()
BOOTSTRAP_MODEL = os.getenv("WASTE_BOOTSTRAP_MODEL", "yolov8n.pt").strip()
