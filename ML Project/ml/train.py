import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 on waste dataset")
    parser.add_argument("--data", type=str, required=True, help="Path to dataset yaml")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--project", type=str, default="runs/waste")
    parser.add_argument("--name", type=str, default="yolov8-waste")
    parser.add_argument("--device", type=str, default="0", help="CUDA device, i.e. 0 or 0,1,2,3 or cpu")
    parser.add_argument("--amp", action="store_true", help="Enable Automatic Mixed Precision (AMP)")
    parser.add_argument(
        "--promote-dir",
        type=str,
        default="models",
        help="Directory where latest promoted checkpoints are stored",
    )
    return parser.parse_args()


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def promote_checkpoints(save_dir: Path, promote_dir: Path) -> None:
    weights_dir = save_dir / "weights"
    best_src = weights_dir / "best.pt"
    last_src = weights_dir / "last.pt"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    checkpoints_root = promote_dir / "checkpoints"
    checkpoint_dir = checkpoints_root / f"{save_dir.name}-{timestamp}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    copied_best = _copy_if_exists(best_src, checkpoint_dir / "best.pt")
    copied_last = _copy_if_exists(last_src, checkpoint_dir / "last.pt")

    # Promote "best.pt" as default model for the API.
    promoted_best = _copy_if_exists(best_src, promote_dir / "best.pt")
    _copy_if_exists(last_src, promote_dir / "last.pt")

    meta = {
        "timestamp": timestamp,
        "save_dir": str(save_dir),
        "checkpoint_dir": str(checkpoint_dir),
        "best_exists": copied_best,
        "last_exists": copied_last,
        "promoted_best": promoted_best,
    }
    with open(promote_dir / "latest_checkpoint.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Checkpoint archive: {checkpoint_dir}")
    print(f"Promoted best model: {promote_dir / 'best.pt'}")
    print(f"Metadata: {promote_dir / 'latest_checkpoint.json'}")


def main():
    args = parse_args()
    model = YOLO(args.model)
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        device=args.device,
        amp=args.amp,
    )
    save_dir = Path(getattr(results, "save_dir", Path(args.project) / args.name))
    promote_dir = Path(args.promote_dir)
    promote_checkpoints(save_dir, promote_dir)


if __name__ == "__main__":
    main()
